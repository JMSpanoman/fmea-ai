"""
Post-market (MAUDE-derived) frequency → suggested FMEA **probability** signals (1–5).

SCIENTIFIC / REGULATORY DISCLAIMER (non-negotiable interpretation):
    MAUDE narrative counts are **not** epidemiological incidence. They are biased by reporting
    behavior, duplicate reports, incomplete narratives, and device coding. Use this engine only
    as **supporting evidence** alongside design history, clinical data, and team judgment when
    adjusting FMEA probability ratings.

FMEA_INTEGRATION:
    - Feed ``suggested_probability_score`` into review workflows for ``FMEARow`` / ``ProjectRiskItem``
      after human acceptance (never auto-write production severity/probability without QMS rules).
    - Pair with ``postmarket_nlp`` extractions and internal complaints for a consolidated PMS picture.

MODULARITY:
    - Tuning: ``PostmarketRiskScoringConfig`` (defaults + optional JSON env override).
    - Aggregation: SQLAlchemy row fetch + in-Python bucketing (clear for SQLite/Postgres).
"""
from __future__ import annotations

import json
import logging
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, List, Optional, Sequence, Set

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.device import Device
from models.fmea import FMEARow
from models.maude_adverse_event import MaudeAdverseEvent
from models.maude_nlp_extraction import MaudeNlpExtraction
from models.project import Project
from models.project_profile import ProjectProfile
from models.project_risk_item import ProjectRiskItem
from services.postmarket_failure_mode_normalize import canonicalize_failure_mode_key
from schemas.postmarket_risk_scoring import (
    ComponentAggregate,
    ConfidenceLevel,
    DeviceFamilyAggregate,
    FailureModeScoreRequest,
    FailureModeScoreResponse,
    PostmarketRiskScoringConfig,
    ProjectRiskScoreItem,
    ProjectRiskScoreResponse,
    RelatedPhraseCount,
    RecentTrend,
    SuggestedMissingRisk,
)

logger = logging.getLogger(__name__)

_ENV_CONFIG_KEY = "POSTMARKET_RISK_SCORING_CONFIG_JSON"


def load_scoring_config() -> PostmarketRiskScoringConfig:
    raw = os.getenv(_ENV_CONFIG_KEY, "").strip()
    if not raw:
        return PostmarketRiskScoringConfig()
    try:
        data = json.loads(raw)
        return PostmarketRiskScoringConfig.model_validate(data)
    except Exception as e:
        logger.warning("Invalid %s; using defaults: %s", _ENV_CONFIG_KEY, e)
        return PostmarketRiskScoringConfig()


def _norm_text(s: Optional[str]) -> str:
    if not s:
        return ""
    t = re.sub(r"\s+", " ", str(s).strip().lower())
    return t


def _failure_mode_key(ex: MaudeNlpExtraction) -> str:
    for cand in (ex.normalized_risk_phrase, ex.failure_mode):
        n = _norm_text(cand)
        if n:
            return canonicalize_failure_mode_key(n)
    return "unknown"


def _outcome_weight(outcome: Optional[str], cfg: PostmarketRiskScoringConfig) -> float:
    o = (outcome or "unknown").strip().lower()
    w = cfg.outcome_weights
    if o == "death":
        return w.death
    if o == "injury":
        return w.injury
    if o == "malfunction":
        return w.malfunction
    if o == "other":
        return w.other
    return w.unknown


def _probability_from_weighted(weighted: float, cfg: PostmarketRiskScoringConfig) -> int:
    t = cfg.probability_thresholds
    if weighted < t.min_weighted_for_2:
        return 1
    if weighted < t.min_weighted_for_3:
        return 2
    if weighted < t.min_weighted_for_4:
        return 3
    if weighted < t.min_weighted_for_5:
        return 4
    return 5


def _trend_from_dates(dates: List[date], cfg: PostmarketRiskScoringConfig) -> RecentTrend:
    valid = sorted({d for d in dates if d is not None})
    if len(valid) < cfg.trend.min_events_per_half * 2:
        return "insufficient_data"
    mid = valid[len(valid) // 2]
    early = [d for d in valid if d < mid]
    late = [d for d in valid if d >= mid]
    if len(early) < cfg.trend.min_events_per_half or len(late) < cfg.trend.min_events_per_half:
        return "insufficient_data"
    e_count, l_count = len(early), len(late)
    if e_count == 0:
        return "increasing" if l_count else "insufficient_data"
    ratio = l_count / e_count
    if ratio >= cfg.trend.increasing_ratio:
        return "increasing"
    if ratio <= cfg.trend.decreasing_ratio:
        return "decreasing"
    return "stable"


def _confidence_level(raw_count: int, window_days: int) -> ConfidenceLevel:
    # Heuristic: more events + longer window → more confidence (still not statistical power).
    density = raw_count / max(window_days, 1)
    if raw_count >= 25 and density >= 0.02:
        return "high"
    if raw_count >= 8:
        return "medium"
    return "low"


def _device_clause(device_type: str):
    dt = device_type.strip()
    if not dt:
        return None
    like = f"%{dt}%"
    return or_(
        MaudeAdverseEvent.generic_name.ilike(like),
        MaudeAdverseEvent.normalized_device_name.ilike(like),
        MaudeAdverseEvent.brand_name.ilike(like),
    )


def _date_clause(date_from: Optional[date], date_to: Optional[date]):
    clauses = []
    if date_from is not None:
        clauses.append(MaudeAdverseEvent.date_received >= date_from)
    if date_to is not None:
        clauses.append(MaudeAdverseEvent.date_received <= date_to)
    if not clauses:
        return None
    return and_(*clauses)


def _device_family_label(ev: MaudeAdverseEvent) -> str:
    """Best available MAUDE device family string for aggregation (generic > normalized > brand)."""
    for cand in (ev.generic_name, ev.normalized_device_name, ev.brand_name):
        n = _norm_text(cand)
        if n:
            return n[:300]
    return "unknown"


@dataclass
class _ScoringRow:
    fm_key: str
    effect: Optional[str]
    cause: Optional[str]
    component: Optional[str]
    outcome: Optional[str]
    date_received: Optional[date]
    weight: float
    device_family: str = "unknown"


def _query_scoring_rows(
    db: Session,
    *,
    device_type: str,
    component: Optional[str],
    failure_mode_substring: Optional[str],
    date_from: Optional[date],
    date_to: Optional[date],
) -> List[_ScoringRow]:
    dc = _device_clause(device_type)
    if dc is None:
        return []

    q = (
        db.query(MaudeNlpExtraction, MaudeAdverseEvent)
        .join(MaudeAdverseEvent, MaudeNlpExtraction.maude_event_id == MaudeAdverseEvent.id)
        .filter(dc)
    )
    dclause = _date_clause(date_from, date_to)
    if dclause is not None:
        q = q.filter(dclause)
    if component and component.strip():
        comp = f"%{component.strip()}%"
        q = q.filter(MaudeNlpExtraction.component.ilike(comp))
    if failure_mode_substring and failure_mode_substring.strip():
        fm = f"%{failure_mode_substring.strip()}%"
        q = q.filter(
            or_(
                MaudeNlpExtraction.failure_mode.ilike(fm),
                MaudeNlpExtraction.normalized_risk_phrase.ilike(fm),
            )
        )

    out: List[_ScoringRow] = []
    cfg = load_scoring_config()
    for ex, ev in q.all():
        key = _failure_mode_key(ex)
        w = _outcome_weight(ex.outcome_classification, cfg)
        out.append(
            _ScoringRow(
                fm_key=key,
                effect=ex.effect,
                cause=ex.cause,
                component=ex.component,
                outcome=ex.outcome_classification,
                date_received=ev.date_received,
                weight=w,
                device_family=_device_family_label(ev),
            )
        )
    return out


def _aggregate_by_failure_mode(rows: Sequence[_ScoringRow]) -> Dict[str, Dict[str, object]]:
    """
    Returns fm_key -> dict with counts, weighted, dates, effect_counter, cause_counter, component_counter
    """
    buckets: Dict[str, Dict[str, object]] = {}
    for r in rows:
        b = buckets.setdefault(
            r.fm_key,
            {
                "raw": 0,
                "weighted": 0.0,
                "dates": [],
                "effects": Counter(),
                "causes": Counter(),
                "components": Counter(),
            },
        )
        b["raw"] = int(b["raw"]) + 1  # type: ignore
        b["weighted"] = float(b["weighted"]) + r.weight  # type: ignore
        if r.date_received:
            b["dates"].append(r.date_received)  # type: ignore
        if r.effect and str(r.effect).strip():
            b["effects"][_norm_text(r.effect)[:500]] += 1  # type: ignore
        if r.cause and str(r.cause).strip():
            b["causes"][_norm_text(r.cause)[:500]] += 1  # type: ignore
        if r.component and str(r.component).strip():
            b["components"][_norm_text(r.component)[:200]] += 1  # type: ignore

    return buckets


def _top_counter(cnt: Counter, n: int = 5) -> List[RelatedPhraseCount]:
    return [RelatedPhraseCount(phrase=k, count=v) for k, v in cnt.most_common(n)]


def _aggregate_device_families(rows: Sequence[_ScoringRow], *, limit: int = 50) -> List[DeviceFamilyAggregate]:
    raw_c: Counter = Counter()
    wt: Dict[str, float] = defaultdict(float)
    for r in rows:
        fam = (r.device_family or "unknown").strip() or "unknown"
        raw_c[fam] += 1
        wt[fam] += r.weight
    ordered = sorted(wt.keys(), key=lambda k: wt[k], reverse=True)[:limit]
    return [
        DeviceFamilyAggregate(
            device_family=k,
            supporting_event_count=raw_c[k],
            weighted_event_count=round(wt[k], 3),
        )
        for k in ordered
    ]


def _aggregate_components_weighted(rows: Sequence[_ScoringRow], *, limit: int = 30) -> List[ComponentAggregate]:
    raw_c: Counter = Counter()
    wt: Dict[str, float] = defaultdict(float)
    for r in rows:
        c = _norm_text(r.component) if r.component else ""
        if not c:
            continue
        key = c[:200]
        raw_c[key] += 1
        wt[key] += r.weight
    ordered = sorted(wt.keys(), key=lambda k: wt[k], reverse=True)[:limit]
    return [
        ComponentAggregate(
            component_text=k,
            supporting_event_count=raw_c[k],
            weighted_event_count=round(wt[k], 3),
        )
        for k in ordered
    ]


def _rationale_text(
    *,
    fm: str,
    raw: int,
    weighted: float,
    trend: RecentTrend,
    score: int,
) -> str:
    return (
        f"MAUDE-derived surveillance theme «{fm}»: {raw} NLP-linked event(s), weighted total {weighted:.2f} "
        f"(injury/death weighted higher than malfunction-only). Recent trend: {trend}. "
        f"Suggested FMEA probability (1–5) = {score}. "
        "This is supporting evidence only—not a measured field failure rate."
    )


def score_failure_mode_request(db: Session, body: FailureModeScoreRequest) -> FailureModeScoreResponse:
    cfg = load_scoring_config()
    date_to = body.date_to
    date_from = body.date_from
    if date_from is None and date_to is None:
        date_to = date.today()
        date_from = date_to - timedelta(days=365 * cfg.default_lookback_years)

    rows = _query_scoring_rows(
        db,
        device_type=body.device_type,
        component=body.component,
        failure_mode_substring=body.failure_mode,
        date_from=date_from,
        date_to=date_to,
    )
    raw_count = len(rows)
    weighted = sum(r.weight for r in rows)
    trend = _trend_from_dates([d for r in rows for d in ([r.date_received] if r.date_received else [])], cfg)
    score = _probability_from_weighted(weighted, cfg)
    window_days = max((date_to - date_from).days, 1) if date_from and date_to else cfg.default_lookback_years * 365
    conf = _confidence_level(raw_count, window_days)

    eff = Counter()
    cau = Counter()
    for r in rows:
        if r.effect and str(r.effect).strip():
            eff[_norm_text(r.effect)[:500]] += 1
        if r.cause and str(r.cause).strip():
            cau[_norm_text(r.cause)[:500]] += 1

    return FailureModeScoreResponse(
        suggested_probability_score=score,
        supporting_event_count=raw_count,
        weighted_event_count=round(weighted, 3),
        recent_trend=trend,
        confidence_level=conf,
        rationale=_rationale_text(fm=body.failure_mode, raw=raw_count, weighted=weighted, trend=trend, score=score),
        top_related_effects=_top_counter(eff),
        top_related_causes=_top_counter(cau),
        device_type=body.device_type,
        component_filter=body.component,
        failure_mode_query=body.failure_mode,
        date_from=date_from,
        date_to=date_to,
    )


def resolve_device_type_for_postmarket(
    db: Session, *, project_id: str, project: Project
) -> str:
    """Public helper: device-type string used for MAUDE corpus filtering for this project."""
    profile = (
        db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    )
    device_type = _derive_device_type_for_project(project, profile)
    if not device_type:
        device_type = _norm_text(project.name) or "device"
    return device_type


def _derive_device_type_for_project(project: Project, profile: Optional[ProjectProfile]) -> str:
    parts: List[str] = []
    if profile:
        if profile.device_description:
            parts.append(profile.device_description[:200])
        if profile.intended_use:
            parts.append(profile.intended_use[:120])
    if project.name:
        parts.append(project.name)
    blob = " ".join(parts).strip()
    if not blob:
        return ""
    # Prefer first "substantive" token sequence (simple heuristic)
    words = re.findall(r"[a-zA-Z0-9][a-zA-Z0-9\-]{2,}", blob)
    if not words:
        return blob[:80]
    # Use longest word as device family hint (e.g. "pacemaker", "infusion")
    words.sort(key=len, reverse=True)
    return words[0][:80]


def _collect_project_failure_norms(db: Session, project_id: str) -> Set[str]:
    norms: Set[str] = set()
    for (fm,) in db.query(FMEARow.failure_mode).filter(FMEARow.project_id == project_id).all():
        n = _norm_text(fm)
        if len(n) >= 3:
            norms.add(n)
            norms.add(canonicalize_failure_mode_key(n))
    dev_ids = [did for (did,) in db.query(Device.id).filter(Device.project_id == project_id).all()]
    if dev_ids:
        for (fm,) in db.query(ProjectRiskItem.failure_mode).filter(ProjectRiskItem.device_id.in_(dev_ids)).all():
            n = _norm_text(fm)
            if len(n) >= 3:
                norms.add(n)
                norms.add(canonicalize_failure_mode_key(n))
    return norms


def _postmarket_covers_fmea(pm_key: str, fmea_norms: Set[str]) -> bool:
    if not pm_key or pm_key == "unknown":
        return True
    if pm_key in fmea_norms:
        return True
    pm_tokens = set(pm_key.split())
    for f in fmea_norms:
        if len(f) >= 5 and (f in pm_key or pm_key in f):
            return True
        ftoks = set(f.split())
        if len(pm_tokens & ftoks) >= 2:
            return True
    return False


def score_project_postmarket(
    db: Session,
    *,
    project_id: str,
    project: Project,
    device_type_override: Optional[str] = None,
    date_from_override: Optional[date] = None,
    date_to_override: Optional[date] = None,
    component_filter: Optional[str] = None,
    failure_mode_filter: Optional[str] = None,
) -> ProjectRiskScoreResponse:
    cfg = load_scoring_config()
    profile = (
        db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()
    )
    ovr = (device_type_override or "").strip()
    if ovr:
        device_type = ovr
    else:
        device_type = _derive_device_type_for_project(project, profile)
        if not device_type:
            device_type = _norm_text(project.name) or "device"

    if date_from_override is not None or date_to_override is not None:
        date_to = date_to_override or date.today()
        date_from = date_from_override or (date_to - timedelta(days=365 * cfg.default_lookback_years))
    else:
        date_to = date.today()
        date_from = date_to - timedelta(days=365 * cfg.default_lookback_years)

    comp_f = (component_filter or "").strip() or None
    fm_f = (failure_mode_filter or "").strip() or None

    rows = _query_scoring_rows(
        db,
        device_type=device_type,
        component=comp_f,
        failure_mode_substring=fm_f,
        date_from=date_from,
        date_to=date_to,
    )
    buckets = _aggregate_by_failure_mode(rows)
    fmea_norms = _collect_project_failure_norms(db, project_id)

    # Sort failure modes by weighted count
    sorted_keys = sorted(
        buckets.keys(),
        key=lambda k: float(buckets[k]["weighted"]),  # type: ignore
        reverse=True,
    )[: cfg.max_failure_modes_returned]

    window_days = max((date_to - date_from).days, 1)
    items: List[ProjectRiskScoreItem] = []
    missing: List[SuggestedMissingRisk] = []

    for fm_key in sorted_keys:
        b = buckets[fm_key]
        raw = int(b["raw"])  # type: ignore
        weighted = float(b["weighted"])  # type: ignore
        dates: List[date] = b["dates"]  # type: ignore
        trend = _trend_from_dates(dates, cfg)
        score = _probability_from_weighted(weighted, cfg)
        conf = _confidence_level(raw, window_days)
        items.append(
            ProjectRiskScoreItem(
                normalized_failure_mode=fm_key,
                suggested_probability_score=score,
                supporting_event_count=raw,
                weighted_event_count=round(weighted, 3),
                recent_trend=trend,
                confidence_level=conf,
                rationale=_rationale_text(fm=fm_key, raw=raw, weighted=weighted, trend=trend, score=score),
                top_related_effects=_top_counter(b["effects"]),  # type: ignore
                top_related_causes=_top_counter(b["causes"]),  # type: ignore
                top_components=_top_counter(b["components"]),  # type: ignore
            )
        )
        if not _postmarket_covers_fmea(fm_key, fmea_norms) and raw >= 3 and fm_key != "unknown":
            missing.append(
                SuggestedMissingRisk(
                    failure_mode_hint=fm_key,
                    weighted_event_count=round(weighted, 3),
                    supporting_event_count=raw,
                    rationale=(
                        f"No strong match in project FMEA / project risk items for «{fm_key}» "
                        f"({raw} post-market NLP-linked events). Consider gap analysis vs design intent."
                    ),
                )
            )

    missing.sort(key=lambda m: m.weighted_event_count, reverse=True)
    missing = missing[:20]

    fam_agg = _aggregate_device_families(rows)
    comp_agg = _aggregate_components_weighted(rows)

    return ProjectRiskScoreResponse(
        project_id=project_id,
        device_type_used=device_type,
        date_from=date_from,
        date_to=date_to,
        config_snapshot=cfg,
        device_family_aggregates=fam_agg,
        component_aggregates=comp_agg,
        items=items,
        suggested_missing_risks=missing,
    )
