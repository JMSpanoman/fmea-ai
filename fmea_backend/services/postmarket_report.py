"""
Assemble a structured post-market report from persisted MAUDE rows and NLP extractions.

ROOT CAUSE (historical “blank PMS Report” in documents):
    The ``pms_report`` document body was filled only by ``_draft_pms_report`` in
    ``project_profile_initializer`` — a deterministic markdown scaffold that never queried
    ``maude_*``, ``pms_signals``, or ``postmarket_project_runs``. Users therefore saw
    “DRAFT — No PMS data included…” even when MAUDE data existed. The API
    ``POST /postmarket/report`` already aggregated real rows but was not used to refresh
    the document. Fix: ``build_pms_report_document_markdown`` reuses the same report
    builder and embeds a data-backed markdown body when ``report_mode == "populated"``.

AGGREGATION:
    Uses the same device/date/component/failure-mode filters as ``risk_scoring._query_scoring_rows``.

ASSUMPTIONS:
    - “Records analyzed” = NLP-linked rows (``maude_nlp_extractions`` joined to ``maude_adverse_events``).
    - Outcome labels come from ``outcome_classification`` on extractions.
"""
from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

from sqlalchemy.orm import Session

from crud import project as project_crud
from models.pms_signal import PMSSignal
from models.postmarket_intelligence import PostmarketProjectRun
from models.project import Project
from schemas.postmarket_report import (
    EvidenceSummaryBlock,
    FilterSummaryBlock,
    MissingRealWorldRiskRow,
    OutcomeBreakdownRow,
    PhraseCountRow,
    PmsSignalIdentifiedRow,
    PostmarketDataSummaryBlock,
    PostmarketReportRequest,
    PostmarketReportResponse,
    PostmarketReportingPeriodBlock,
    PostmarketTopFindingsBlock,
    ProjectSummaryBlock,
    RecommendedFmeaDraftRow,
    ReportTopFailureModeRow,
    TrendPeriodRow,
    TrendSummaryBlock,
)
from services.risk_scoring import (
    _ScoringRow,
    _aggregate_by_failure_mode,
    _norm_text,
    _probability_from_weighted,
    _query_scoring_rows,
    load_scoring_config,
    resolve_device_type_for_postmarket,
    score_project_postmarket,
)

logger = logging.getLogger(__name__)

_OUTCOMES = ("malfunction", "injury", "death", "other", "unknown")

STANDARD_DISCLAIMER = (
    "FDA MAUDE and openFDA data are supportive evidence only: extracts may be incomplete, duplicated, "
    "or under-reported. Counts and themes in this report do not represent true device incidence and "
    "must not replace clinical, quality, or regulatory judgment. Findings require documented expert "
    "review before any update to probability scores, labeling, usability files, or the risk management file."
)


def _coerce_outcome(raw: Optional[str]) -> str:
    o = (raw or "unknown").strip().lower()
    if o in _OUTCOMES:
        return o
    return "other" if o else "unknown"


def _phrase_rows(cnt: Counter, total: int, limit: int) -> List[PhraseCountRow]:
    rows: List[PhraseCountRow] = []
    for phrase, c in cnt.most_common(limit):
        pct = round(100.0 * c / total, 2) if total else None
        rows.append(PhraseCountRow(phrase=phrase, count=c, percentage_of_analyzed=pct))
    return rows


def _phrase_rows_simple(cnt: Counter, limit: int) -> List[PhraseCountRow]:
    rows: List[PhraseCountRow] = []
    for phrase, c in cnt.most_common(limit):
        rows.append(PhraseCountRow(phrase=phrase, count=c, percentage_of_analyzed=None))
    return rows


def _month_key(d: date) -> str:
    return f"{d.year}-{d.month:02d}"


def _quarter_key(d: date) -> str:
    q = (d.month - 1) // 3 + 1
    return f"{d.year}-Q{q}"


def _build_trend_periods(
    dates: List[date],
    *,
    date_from: Optional[date],
    date_to: Optional[date],
) -> Tuple[str, List[TrendPeriodRow], str]:
    valid = [d for d in dates if d is not None]
    if not valid:
        return "monthly", [], "Insufficient dated records to summarize a time trend in analyzed data."

    start = min(valid)
    end = max(valid)
    span_days = (end - start).days + 1
    use_quarterly = span_days > 730
    bucket: Dict[str, int] = defaultdict(int)
    for d in valid:
        key = _quarter_key(d) if use_quarterly else _month_key(d)
        bucket[key] += 1
    ordered = sorted(bucket.keys())
    periods = [TrendPeriodRow(period_label=k, event_count=bucket[k]) for k in ordered]
    gran = "quarterly" if use_quarterly else "monthly"
    qual = (
        f"Reported events in analyzed records are distributed across {len(periods)} {gran} period(s). "
        "This pattern is descriptive only and does not establish causality or statistical control limits."
    )
    return gran, periods, qual


def _dt_start_utc(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def _dt_end_utc(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)


def _query_pms_signals_for_project(
    db: Session,
    *,
    project_id: str,
    date_from: Optional[date],
    date_to: Optional[date],
) -> List[PMSSignal]:
    q = db.query(PMSSignal).filter(PMSSignal.project_id == project_id)
    if date_from is not None:
        q = q.filter(PMSSignal.date_detected >= _dt_start_utc(date_from))
    if date_to is not None:
        q = q.filter(PMSSignal.date_detected <= _dt_end_utc(date_to))
    return q.order_by(PMSSignal.date_detected.desc()).all()


def _pms_signal_ui_status(sig: PMSSignal) -> str:
    st = (sig.status or "").lower()
    if st == "closed":
        return "closed"
    if (sig.trigger_status or "") == "capa_required":
        return "escalated"
    if (sig.trigger_status or "") == "risk_review_required":
        return "under_review"
    if (sig.trend_status or "") == "confirmed":
        return "assessed"
    if (sig.trend_status or "") == "false_alarm":
        return "closed"
    if st == "investigating":
        return "under_review"
    if st == "open":
        return "new"
    return "monitor"


def _pms_rows_to_signal_models(signals: List[PMSSignal]) -> List[PmsSignalIdentifiedRow]:
    out: List[PmsSignalIdentifiedRow] = []
    for sig in signals:
        desc = (sig.title or "").strip()
        if sig.description and str(sig.description).strip():
            desc = f"{desc}: {sig.description}".strip(": ").strip()
        src_parts = [p for p in (sig.signal_type, sig.source_ref) if p and str(p).strip()]
        source = " | ".join(src_parts) if src_parts else "pms_signal"
        notes = (sig.recommended_action or "").strip() or None
        out.append(
            PmsSignalIdentifiedRow(
                signal_id=(sig.signal_key or sig.id)[:80],
                description=desc or "(no title)",
                source=source,
                status=_pms_signal_ui_status(sig),
                notes=notes,
            )
        )
    return out


def _synthetic_maude_theme_signals(top_fm_keys: List[str], *, limit: int = 8) -> List[PmsSignalIdentifiedRow]:
    rows: List[PmsSignalIdentifiedRow] = []
    for i, fm in enumerate(top_fm_keys[:limit]):
        if not fm or fm == "unknown":
            continue
        rows.append(
            PmsSignalIdentifiedRow(
                signal_id=f"MAUDE-THEME-{i + 1:02d}",
                description=(
                    f"Post-market narrative theme observed in MAUDE NLP extractions: {fm}. "
                    "Phrasing reflects reporter language; expert review required before causal inference."
                ),
                source="MAUDE NLP / openFDA-derived extractions",
                status="monitor",
                notes="Derived from aggregated failure-mode counts in the selected filter window.",
            )
        )
    return rows


def _latest_postmarket_run(db: Session, project_id: str) -> Optional[PostmarketProjectRun]:
    return (
        db.query(PostmarketProjectRun)
        .filter(PostmarketProjectRun.project_id == project_id)
        .order_by(PostmarketProjectRun.started_at.desc())
        .first()
    )


def _has_meaningful_scoring_summary(run: Optional[PostmarketProjectRun]) -> bool:
    if not run or run.scoring_summary is None:
        return False
    ss = run.scoring_summary
    if isinstance(ss, dict) and not ss:
        return False
    return True


def _signals_from_pipeline_missing(run: Optional[PostmarketProjectRun]) -> List[PmsSignalIdentifiedRow]:
    if not run or not run.top_missing_risks:
        return []
    raw = run.top_missing_risks
    if not isinstance(raw, list):
        return []
    out: List[PmsSignalIdentifiedRow] = []
    for i, m in enumerate(raw[:15]):
        if not isinstance(m, dict):
            continue
        hint = (m.get("failure_mode_hint") or "").strip()
        if not hint:
            continue
        rationale = (m.get("rationale") or "").strip()
        out.append(
            PmsSignalIdentifiedRow(
                signal_id=f"PIPELINE-MISSING-{i + 1:02d}",
                description=f"Potential gap vs project FMEA themes: {hint}",
                source="postmarket_project_runs.top_missing_risks",
                status="under_review",
                notes=rationale[:2000] if rationale else None,
            )
        )
    return out


def _missing_from_pipeline_json(
    run: Optional[PostmarketProjectRun],
    *,
    component_filter: Optional[str],
) -> Tuple[List[MissingRealWorldRiskRow], List[RecommendedFmeaDraftRow]]:
    miss: List[MissingRealWorldRiskRow] = []
    drafts: List[RecommendedFmeaDraftRow] = []
    if not run or not run.top_missing_risks or not isinstance(run.top_missing_risks, list):
        return miss, drafts
    for m in run.top_missing_risks[:25]:
        if not isinstance(m, dict):
            continue
        hint = (m.get("failure_mode_hint") or "").strip()
        if not hint:
            continue
        sec = int(m.get("supporting_event_count") or 0)
        w = m.get("weighted_event_count")
        wt = float(w) if w is not None else None
        rationale = (m.get("rationale") or "Identified in last post-market pipeline run; expert review required.").strip()
        miss.append(
            MissingRealWorldRiskRow(
                normalized_failure_mode=hint,
                component=component_filter,
                supporting_event_count=sec,
                rationale=rationale,
                add_to_fmea_available=True,
                requires_expert_review=True,
            )
        )
        drafts.append(
            RecommendedFmeaDraftRow(
                normalized_failure_mode=hint,
                supporting_event_count=sec,
                weighted_event_count=wt,
                rationale=rationale,
                requires_expert_review=True,
                add_to_fmea_available=True,
            )
        )
    return miss, drafts


def _global_component_counter(rows: List[_ScoringRow]) -> Counter:
    c: Counter = Counter()
    for r in rows:
        if r.component and str(r.component).strip():
            c[_norm_text(r.component)[:200]] += 1
    return c


def _unique_failure_mode_count(rows: List[_ScoringRow]) -> int:
    keys = {r.fm_key for r in rows if r.fm_key and r.fm_key != "unknown"}
    return len(keys)


def _recommended_actions(*, populated: bool) -> List[str]:
    if populated:
        return [
            "Review project FMEA coverage against the top post-market themes; treat any suggested additions as draft inputs pending expert adjudication.",
            "Assess whether occurrence / probability scoring in the risk file remains appropriate given the descriptive themes in this window (not incidence rates).",
            "Evaluate whether CAPA, additional monitoring, or supplier engagement is warranted where injury, death, or escalating complaint-like malfunction patterns appear.",
            "Where use-related or labeling patterns appear in narratives, review IFU, training, and human factors assumptions before concluding residual risk.",
        ]
    return [
        "Ingest MAUDE/openFDA device events aligned with this project’s device type, then run NLP extraction so linked narrative rows exist for reporting.",
        "Optionally run the orchestrated post-market pipeline to persist scoring snapshots and suggested missing-risk themes.",
        "Record formal PMS signals (complaints, vigilance, service) in the PMS signal register when internal data are available.",
    ]


def _resolve_project(db: Session, project_id: str, user_id: Optional[str]) -> Optional[Project]:
    if user_id:
        return project_crud.get_project(db, project_id, user_id)
    return project_crud.get_project_by_id(db, project_id)


def _safe_query_scoring_rows(
    db: Session,
    *,
    device_type: str,
    component: Optional[str],
    failure_mode_substring: Optional[str],
    date_from: Optional[date],
    date_to: Optional[date],
    project_id: str,
) -> List[_ScoringRow]:
    try:
        return _query_scoring_rows(
            db,
            device_type=device_type,
            component=component,
            failure_mode_substring=failure_mode_substring,
            date_from=date_from,
            date_to=date_to,
        )
    except Exception:
        logger.exception(
            "postmarket report: _query_scoring_rows failed project=%s device_type=%s",
            project_id,
            device_type,
        )
        return []


def _safe_query_pms_signals(
    db: Session,
    *,
    project_id: str,
    date_from: Optional[date],
    date_to: Optional[date],
) -> List[PMSSignal]:
    try:
        return _query_pms_signals_for_project(db, project_id=project_id, date_from=date_from, date_to=date_to)
    except Exception:
        logger.exception("postmarket report: PMS signals query failed project=%s", project_id)
        return []


def _safe_latest_postmarket_run(db: Session, project_id: str) -> Optional[PostmarketProjectRun]:
    try:
        return _latest_postmarket_run(db, project_id)
    except Exception:
        logger.exception("postmarket report: postmarket_project_runs query failed project=%s", project_id)
        return None


def _safe_resolve_device_type(db: Session, project: Project, body: PostmarketReportRequest) -> str:
    explicit = (body.device_type or "").strip()
    if explicit:
        return explicit
    try:
        return resolve_device_type_for_postmarket(db, project_id=body.project_id, project=project)
    except Exception:
        logger.exception("postmarket report: resolve_device_type_for_postmarket failed project=%s", body.project_id)
        return (project.name or "device")[:80]


def _minimal_postmarket_report_response(
    db: Session,
    *,
    project: Project,
    body: PostmarketReportRequest,
    error: Optional[Exception] = None,
) -> PostmarketReportResponse:
    """
    Valid draft-shaped response when the full aggregation path fails (missing tables, join errors, etc.).
    Never omits required fields expected by clients.
    """
    cfg = load_scoring_config()
    date_to = body.date_to
    date_from = body.date_from
    if date_from is None and date_to is None:
        date_to = date.today()
        date_from = date_to - timedelta(days=365 * cfg.default_lookback_years)
    elif date_from is None and date_to is not None:
        date_from = date_to - timedelta(days=365 * cfg.default_lookback_years)
    elif date_to is None and date_from is not None:
        date_to = date.today()

    device_type = _safe_resolve_device_type(db, project, body)
    qual = (
        "No NLP-linked MAUDE records matched the current filters for this report scope. "
        "Consider ingest, NLP extraction, or broadening filters."
    )
    if error is not None:
        qual += f" (Report aggregation degraded: {type(error).__name__}: {error})"

    err_note = str(error) if error else ""
    trend_block: Optional[TrendSummaryBlock] = None
    if body.include_trend_summary:
        gran, periods, qual_trend = _build_trend_periods([], date_from=date_from, date_to=date_to)
        trend_block = TrendSummaryBlock(granularity=gran, periods=periods, qualitative_summary=qual_trend)

    outcome_rows: List[OutcomeBreakdownRow] = []
    if body.include_outcome_breakdown:
        for o in _OUTCOMES:
            outcome_rows.append(OutcomeBreakdownRow(outcome=o, count=0, percentage=0.0))

    period_label = f"{date_from.isoformat() if date_from else '—'} to {date_to.isoformat() if date_to else '—'} (filter window; UTC boundaries for PMS signals)"

    summary_block = PostmarketDataSummaryBlock(
        maude_nlp_linked_records_reviewed=0,
        pms_signal_records_in_scope=0,
        unique_normalized_failure_modes=0,
        malfunction_outcome_events=0,
        injury_outcome_events=0,
        death_outcome_events=0,
        other_outcome_events=0,
        unknown_outcome_events=0,
        date_range_analyzed_start=date_from,
        date_range_analyzed_end=date_to,
    )
    top_findings = PostmarketTopFindingsBlock(
        top_failure_modes=[],
        top_causes=[],
        top_effects=[],
        top_components=[],
        trend_qualitative=trend_block.qualitative_summary if trend_block else None,
    )

    logger.warning(
        "postmarket report: returning minimal draft project=%s device_type=%s error=%s",
        body.project_id,
        device_type,
        err_note[:500] if err_note else "",
    )

    return PostmarketReportResponse(
        report_mode="draft",
        report_title="PMS Report — Draft",
        generated_at=datetime.now(timezone.utc),
        project_summary=ProjectSummaryBlock(
            project_id=project.id,
            project_name=project.name,
            project_description=project.description,
        ),
        filter_summary=FilterSummaryBlock(
            device_type_used=device_type,
            device_name_label=(body.device_name or "").strip() or None,
            component_filter=(body.component or "").strip() or None,
            failure_mode_filter=(body.failure_mode or "").strip() or None,
            date_from=date_from,
            date_to=date_to,
        ),
        reporting_period=PostmarketReportingPeriodBlock(
            date_from=date_from,
            date_to=date_to,
            label=period_label,
            markets_regions_note=None,
        ),
        summary=summary_block,
        top_findings=top_findings,
        signals_identified=[],
        recommended_actions=_recommended_actions(populated=False),
        evidence_summary=EvidenceSummaryBlock(
            total_maude_records_analyzed=0,
            date_range_analyzed_start=date_from,
            date_range_analyzed_end=date_to,
            qualitative_summary=qual,
            component_focus_note=None,
        ),
        top_failure_modes=[],
        top_causes=[],
        top_effects=[],
        outcome_breakdown=outcome_rows,
        trend_summary=trend_block,
        missing_real_world_risks=[],
        recommended_fmea_drafts=[],
        disclaimer=STANDARD_DISCLAIMER,
    )


def build_postmarket_report(
    db: Session,
    *,
    user_id: Optional[str],
    body: PostmarketReportRequest,
) -> PostmarketReportResponse:
    try:
        payload = body.model_dump(mode="json", default=str)
    except Exception:
        try:
            payload = body.model_dump()
        except Exception:
            payload = {"project_id": getattr(body, "project_id", "")}
    logger.info(
        "postmarket report request project=%s payload=%s",
        body.project_id,
        json.dumps(payload, default=str)[:8000],
    )
    try:
        return _build_postmarket_report_inner(db, user_id=user_id, body=body)
    except ValueError:
        raise
    except Exception as e:
        logger.exception(
            "postmarket report: inner build failed project=%s user=%s",
            body.project_id,
            user_id or "(system)",
        )
        project = _resolve_project(db, body.project_id, user_id)
        if not project:
            raise ValueError("Project not found") from e
        return _minimal_postmarket_report_response(db, project=project, body=body, error=e)


def _build_postmarket_report_inner(
    db: Session,
    *,
    user_id: Optional[str],
    body: PostmarketReportRequest,
) -> PostmarketReportResponse:
    project = _resolve_project(db, body.project_id, user_id)
    if not project:
        uid = user_id or "(system)"
        logger.warning("postmarket report: project not found user=%s project=%s", uid, body.project_id)
        raise ValueError("Project not found")

    cfg = load_scoring_config()
    device_type = _safe_resolve_device_type(db, project, body)

    date_to = body.date_to
    date_from = body.date_from
    if date_from is None and date_to is None:
        date_to = date.today()
        date_from = date_to - timedelta(days=365 * cfg.default_lookback_years)
    elif date_from is None and date_to is not None:
        date_from = date_to - timedelta(days=365 * cfg.default_lookback_years)
    elif date_to is None and date_from is not None:
        date_to = date.today()

    rows = _safe_query_scoring_rows(
        db,
        device_type=device_type,
        component=(body.component or "").strip() or None,
        failure_mode_substring=(body.failure_mode or "").strip() or None,
        date_from=date_from,
        date_to=date_to,
        project_id=body.project_id,
    )
    n = len(rows)

    pms_signals = _safe_query_pms_signals(
        db, project_id=body.project_id, date_from=date_from, date_to=date_to
    )
    pms_signal_count = len(pms_signals)
    latest_run = _safe_latest_postmarket_run(db, body.project_id)
    has_ss = _has_meaningful_scoring_summary(latest_run)

    report_mode: Literal["populated", "draft"] = "draft"
    if n > 0 or pms_signal_count > 0 or has_ss:
        report_mode = "populated"

    logger.info(
        "postmarket report project=%s device_type=%s nlp_linked_rows=%s pms_signals=%s "
        "scoring_summary_present=%s report_mode=%s",
        body.project_id,
        device_type,
        n,
        pms_signal_count,
        has_ss,
        report_mode,
    )

    dates_for_range = [r.date_received for r in rows if r.date_received]
    dr_start = min(dates_for_range) if dates_for_range else date_from
    dr_end = max(dates_for_range) if dates_for_range else date_to

    outcome_c: Counter = Counter()
    global_effects: Counter = Counter()
    global_causes: Counter = Counter()
    global_components = _global_component_counter(rows)
    for r in rows:
        outcome_c[_coerce_outcome(r.outcome)] += 1
        if r.effect and str(r.effect).strip():
            global_effects[_norm_text(r.effect)[:500]] += 1
        if r.cause and str(r.cause).strip():
            global_causes[_norm_text(r.cause)[:500]] += 1

    outcome_rows: List[OutcomeBreakdownRow] = []
    if body.include_outcome_breakdown:
        for o in _OUTCOMES:
            c = int(outcome_c.get(o, 0))
            pct = round(100.0 * c / n, 2) if n else 0.0
            outcome_rows.append(OutcomeBreakdownRow(outcome=o, count=c, percentage=pct))

    buckets = _aggregate_by_failure_mode(rows)
    sorted_fms = sorted(
        buckets.keys(),
        key=lambda k: int(buckets[k]["raw"]),  # type: ignore[arg-type]
        reverse=True,
    )
    top_fm_keys = [k for k in sorted_fms if k and k != "unknown"][: body.max_failure_modes]

    top_failure_modes: List[ReportTopFailureModeRow] = []
    fm_counter_for_top: Counter = Counter()
    for fm_key in top_fm_keys:
        b = buckets[fm_key]
        raw = int(b["raw"])  # type: ignore[arg-type]
        fm_counter_for_top[fm_key] = raw
        weighted = float(b["weighted"])  # type: ignore[arg-type]
        score = _probability_from_weighted(weighted, cfg)
        eff: Counter = b["effects"]  # type: ignore[assignment]
        cau: Counter = b["causes"]  # type: ignore[assignment]
        comp: Counter = b["components"]  # type: ignore[assignment]
        top_failure_modes.append(
            ReportTopFailureModeRow(
                normalized_failure_mode=fm_key,
                supporting_event_count=raw,
                weighted_event_count=round(weighted, 4),
                top_related_components=_phrase_rows(comp, raw, min(5, body.max_phrase_rows)),
                top_related_effects=_phrase_rows(eff, raw, min(5, body.max_phrase_rows)),
                top_related_causes=_phrase_rows(cau, raw, min(5, body.max_phrase_rows)),
                suggested_probability_score=score,
            )
        )

    trend_block: Optional[TrendSummaryBlock] = None
    trend_qual: Optional[str] = None
    if body.include_trend_summary:
        gran, periods, qual = _build_trend_periods(dates_for_range, date_from=date_from, date_to=date_to)
        trend_qual = qual
        trend_block = TrendSummaryBlock(granularity=gran, periods=periods, qualitative_summary=qual)

    comp_note: Optional[str] = None
    if body.component and body.component.strip():
        comp_note = (
            f"Analysis is filtered to NLP extractions whose component field suggests a match to "
            f"«{body.component.strip()}». Phrasing varies by reporter; this is a heuristic filter."
        )

    qual_evidence = (
        f"Analyzed {n} MAUDE-linked narrative extraction(s) for device-type filter «{device_type}». "
        "Reported events suggest the themes below are commonly observed in this filtered corpus; "
        "supporting post-market evidence indicates priorities for expert review, not confirmed root causes."
    )
    if n == 0:
        qual_evidence = (
            "No NLP-linked MAUDE records matched the current filters for this report scope. "
            "Consider broadening device type or date range, completing ingest/NLP extraction, or aligning filters with the last post-market pipeline run."
        )
        if has_ss and latest_run and isinstance(latest_run.scoring_summary, dict):
            ss = latest_run.scoring_summary
            qual_evidence += (
                f" A stored post-market pipeline scoring snapshot exists (failure-mode themes scored: "
                f"{ss.get('failure_mode_themes_scored', '—')}; suggested missing themes: "
                f"{ss.get('suggested_missing_count', '—')}). Counts in this narrative section may be zero if "
                "filters differ from that run."
            )

    missing_list: List[MissingRealWorldRiskRow] = []
    draft_list: List[RecommendedFmeaDraftRow] = []
    if body.include_missing_risks:
        if n > 0:
            try:
                score_resp = score_project_postmarket(
                    db,
                    project_id=body.project_id,
                    project=project,
                    device_type_override=device_type,
                    date_from_override=date_from,
                    date_to_override=date_to,
                    component_filter=(body.component or "").strip() or None,
                    failure_mode_filter=(body.failure_mode or "").strip() or None,
                )
                for m in score_resp.suggested_missing_risks:
                    missing_list.append(
                        MissingRealWorldRiskRow(
                            normalized_failure_mode=m.failure_mode_hint,
                            component=(body.component or "").strip() if body.component else None,
                            supporting_event_count=m.supporting_event_count,
                            rationale=m.rationale,
                            add_to_fmea_available=True,
                            requires_expert_review=True,
                        )
                    )
                    draft_list.append(
                        RecommendedFmeaDraftRow(
                            normalized_failure_mode=m.failure_mode_hint,
                            supporting_event_count=m.supporting_event_count,
                            weighted_event_count=m.weighted_event_count,
                            rationale=m.rationale,
                            requires_expert_review=True,
                            add_to_fmea_available=True,
                        )
                    )
            except Exception:
                logger.exception("postmarket report: missing-risk section failed")
                missing_list = []
                draft_list = []
        elif latest_run:
            miss2, draft2 = _missing_from_pipeline_json(
                latest_run,
                component_filter=(body.component or "").strip() or None,
            )
            missing_list = miss2
            draft_list = draft2

    signals_identified: List[PmsSignalIdentifiedRow] = []
    signals_identified.extend(_pms_rows_to_signal_models(pms_signals))
    if n > 0:
        existing_lower = {s.description[:120].lower() for s in signals_identified}
        for syn in _synthetic_maude_theme_signals(top_fm_keys, limit=8):
            if syn.description[:120].lower() in existing_lower:
                continue
            signals_identified.append(syn)
            existing_lower.add(syn.description[:120].lower())
    if n == 0 and not signals_identified:
        signals_identified.extend(_signals_from_pipeline_missing(latest_run))

    period_label = f"{date_from.isoformat() if date_from else '—'} to {date_to.isoformat() if date_to else '—'} (filter window; UTC boundaries for PMS signals)"

    summary_block = PostmarketDataSummaryBlock(
        maude_nlp_linked_records_reviewed=n,
        pms_signal_records_in_scope=pms_signal_count,
        unique_normalized_failure_modes=_unique_failure_mode_count(rows),
        malfunction_outcome_events=int(outcome_c.get("malfunction", 0)),
        injury_outcome_events=int(outcome_c.get("injury", 0)),
        death_outcome_events=int(outcome_c.get("death", 0)),
        other_outcome_events=int(outcome_c.get("other", 0)),
        unknown_outcome_events=int(outcome_c.get("unknown", 0)),
        date_range_analyzed_start=dr_start if isinstance(dr_start, date) else None,
        date_range_analyzed_end=dr_end if isinstance(dr_end, date) else None,
    )

    top_findings = PostmarketTopFindingsBlock(
        top_failure_modes=_phrase_rows_simple(fm_counter_for_top, body.max_failure_modes),
        top_causes=_phrase_rows_simple(global_causes, body.max_phrase_rows),
        top_effects=_phrase_rows_simple(global_effects, body.max_phrase_rows),
        top_components=_phrase_rows_simple(global_components, body.max_phrase_rows),
        trend_qualitative=trend_qual,
    )

    report_title = (
        "Post-Market Surveillance Report (data-backed)"
        if report_mode == "populated"
        else "PMS Report — Draft"
    )

    return PostmarketReportResponse(
        report_mode=report_mode,
        report_title=report_title,
        generated_at=datetime.now(timezone.utc),
        project_summary=ProjectSummaryBlock(
            project_id=project.id,
            project_name=project.name,
            project_description=project.description,
        ),
        filter_summary=FilterSummaryBlock(
            device_type_used=device_type,
            device_name_label=(body.device_name or "").strip() or None,
            component_filter=(body.component or "").strip() or None,
            failure_mode_filter=(body.failure_mode or "").strip() or None,
            date_from=date_from,
            date_to=date_to,
        ),
        reporting_period=PostmarketReportingPeriodBlock(
            date_from=date_from,
            date_to=date_to,
            label=period_label,
            markets_regions_note=None,
        ),
        summary=summary_block,
        top_findings=top_findings,
        signals_identified=signals_identified,
        recommended_actions=_recommended_actions(populated=(report_mode == "populated")),
        evidence_summary=EvidenceSummaryBlock(
            total_maude_records_analyzed=n,
            date_range_analyzed_start=dr_start if isinstance(dr_start, date) else None,
            date_range_analyzed_end=dr_end if isinstance(dr_end, date) else None,
            qualitative_summary=qual_evidence,
            component_focus_note=comp_note,
        ),
        top_failure_modes=top_failure_modes,
        top_causes=_phrase_rows(global_causes, n, body.max_phrase_rows),
        top_effects=_phrase_rows(global_effects, n, body.max_phrase_rows),
        outcome_breakdown=outcome_rows,
        trend_summary=trend_block,
        missing_real_world_risks=missing_list,
        recommended_fmea_drafts=draft_list,
        disclaimer=STANDARD_DISCLAIMER,
    )


def _ref_line(label: str, doc: Any, doc_type: str) -> str:
    if not doc:
        return f"- {label}: (type={doc_type}) — (not present yet)"
    return (
        f"- {label}: doc_id={getattr(doc, 'id', '')} "
        f"(type={doc_type}, status={getattr(doc, 'status', '')}, version=v{getattr(doc, 'version', '')})"
    )


def render_postmarket_report_markdown(resp: PostmarketReportResponse, *, refs: Optional[Dict[str, Any]] = None) -> str:
    """Serialize a structured report to markdown suitable for the ``pms_report`` document body."""
    refs = refs or {}
    lines: List[str] = []
    ps = resp.project_summary
    lines.append(resp.report_title)
    lines.append("")
    lines.append(f"Project ID: {ps.project_id}")
    lines.append(f"Project name: {ps.project_name}")
    lines.append(f"Generated at (UTC): {resp.generated_at.isoformat()}")
    lines.append(f"Report mode: {resp.report_mode}")
    lines.append(f"Reporting period: {resp.reporting_period.label}")
    if resp.reporting_period.markets_regions_note:
        lines.append(f"Markets / regions: {resp.reporting_period.markets_regions_note}")
    lines.append("")
    lines.append("## Summary of data reviewed")
    s = resp.summary
    lines.append(f"- MAUDE NLP-linked records in scope: {s.maude_nlp_linked_records_reviewed}")
    lines.append(f"- PMS signal records in scope (project register): {s.pms_signal_records_in_scope}")
    lines.append(f"- Unique normalized failure modes (extracted): {s.unique_normalized_failure_modes}")
    lines.append(f"- Malfunction-classified narrative rows: {s.malfunction_outcome_events}")
    lines.append(f"- Injury-classified narrative rows: {s.injury_outcome_events}")
    lines.append(f"- Death-classified narrative rows: {s.death_outcome_events}")
    lines.append(
        f"- Date range in analyzed MAUDE rows: "
        f"{s.date_range_analyzed_start or '—'} → {s.date_range_analyzed_end or '—'}"
    )
    lines.append("")
    lines.append(resp.evidence_summary.qualitative_summary)
    lines.append("")
    if resp.report_mode == "draft":
        lines.append(
            "**DRAFT — No qualifying post-market corpus matched this report scope.** "
            "Populate after ingest, NLP extraction, PMS signals, and/or a completed post-market pipeline run."
        )
        lines.append("")
    lines.append("## Top findings (counts)")
    tf = resp.top_findings
    lines.append("### Failure modes")
    for r in tf.top_failure_modes[:15]:
        lines.append(f"- {r.phrase}: {r.count}")
    if not tf.top_failure_modes:
        lines.append("- (none in scope)")
    lines.append("### Top causes (corpus)")
    for r in tf.top_causes[:15]:
        lines.append(f"- {r.phrase}: {r.count}")
    lines.append("### Top effects (corpus)")
    for r in tf.top_effects[:15]:
        lines.append(f"- {r.phrase}: {r.count}")
    lines.append("### Top components (corpus)")
    for r in tf.top_components[:15]:
        lines.append(f"- {r.phrase}: {r.count}")
    if tf.trend_qualitative:
        lines.append("### Trend (qualitative)")
        lines.append(tf.trend_qualitative)
    lines.append("")
    lines.append("## Signals identified")
    lines.append("| signal_id | description | source | status | notes |")
    lines.append("| --- | --- | --- | --- | --- |")
    for sig in resp.signals_identified:
        desc = (sig.description or "").replace("|", "\\|")
        notes = (sig.notes or "").replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {sig.signal_id} | {desc[:500]} | {sig.source} | {sig.status} | {notes[:300]} |"
        )
    if not resp.signals_identified:
        lines.append("| — | — | — | — | — |")
    lines.append("")
    lines.append("## Missing real-world risks (expert review required)")
    for m in resp.missing_real_world_risks[:25]:
        comp = f"; component hint: {m.component}" if m.component else ""
        lines.append(
            f"- **{m.normalized_failure_mode}** — {m.supporting_event_count} supporting events{comp}. {m.rationale}"
        )
    if not resp.missing_real_world_risks:
        lines.append("- None listed for this scope.")
    lines.append("")
    lines.append("## Recommended actions")
    for a in resp.recommended_actions:
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Disclaimer")
    lines.append(resp.disclaimer)
    lines.append("")
    lines.append("## References")
    lines.append(_ref_line("PMS Plan", refs.get("pms_plan"), "pms_plan"))
    lines.append(_ref_line("Hazard Analysis", refs.get("hazard_analysis"), "hazard_analysis"))
    lines.append(_ref_line("FMEA", refs.get("fmea"), "fmea"))
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_pms_report_document_markdown(
    db: Session,
    *,
    project_id: str,
    refs: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Build markdown for the ``pms_report`` document using the same aggregation rules as the API.
    Called from project initialization / profile refresh (no end-user context).
    """
    body = PostmarketReportRequest(
        project_id=project_id,
        include_missing_risks=True,
        include_trend_summary=True,
        include_outcome_breakdown=True,
    )
    resp = build_postmarket_report(db, user_id=None, body=body)
    return render_postmarket_report_markdown(resp, refs=refs)
