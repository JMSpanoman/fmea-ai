"""
Post-market MAUDE narrative → structured risk extraction (OpenAI).

DOWNSTREAM_FMEA_INTEGRATION (future):
    - Map ``failure_mode``, ``cause``, ``effect``, ``harm``, and ``normalized_risk_phrase`` to
      ``ProjectRiskItem`` / ``HazardAnalysisItem`` candidates using rule tables (e.g. keyword →
      hazard category) or the existing ``risk_rule_engine`` after admin review.
    - Use ``outcome_classification`` + frequency from multiple events to prioritize residual risk
      reviews and PMS signal detection thresholds (stored in DB per IMPLEMENTATION_RULES).

DOWNSTREAM_RECALLS_COMPLAINTS (future):
    - Same extraction schema can be reused for FDA recall narratives and internal complaint text
      with ``source_system`` on the parent record; keep prompts source-specific if needed.

Example LLM outputs (illustrative; real model output may vary):

**Narrative 1:** "Device displayed low battery warning but shut down during infusion. Patient received
partial dose. No injury reported."

```json
{
  "failure_mode": "unexpected shutdown during use",
  "cause": "battery depletion during active use",
  "effect": "partial dose delivered to patient",
  "component": "battery / power subsystem",
  "harm": null,
  "outcome_classification": "malfunction",
  "confidence_score": 0.78,
  "normalized_risk_phrase": "incomplete dose delivery"
}
```

**Narrative 2:** "Lead fracture noted on X-ray. Patient experienced syncopal episodes requiring
hospitalization."

```json
{
  "failure_mode": "lead fracture",
  "cause": null,
  "effect": "syncope and hospitalization",
  "component": "implantable lead",
  "harm": "syncopal episodes",
  "outcome_classification": "injury",
  "confidence_score": 0.82,
  "normalized_risk_phrase": "lead structural failure with patient injury"
}
```

**Narrative 3:** "Reporter stated device did not turn on. Information insufficient for analysis."

```json
{
  "failure_mode": "device failed to power on",
  "cause": null,
  "effect": "therapy not delivered",
  "component": null,
  "harm": null,
  "outcome_classification": "unknown",
  "confidence_score": 0.45,
  "normalized_risk_phrase": "power-on failure"
}
```
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from crud import maude_nlp_extraction as nlp_crud
from models.maude_adverse_event import MaudeAdverseEvent
from schemas.postmarket_nlp import (
    EventExtractResult,
    MaudeNarrativeLlmExtract,
    PostmarketExtractRequest,
    PostmarketExtractResponse,
)

logger = logging.getLogger(__name__)

ALLOWED_OUTCOMES = frozenset({"malfunction", "injury", "death", "other", "unknown"})

# --- LLM prompt template (edit cautiously; keep "no invention" rules) ---

MAUDE_NLP_SYSTEM_PROMPT = """You are a clinical safety analyst extracting structured risk information
from FDA MAUDE-style adverse event narratives for a medical device QMS.

Rules:
1. Use ONLY information explicitly or clearly implied in the narrative. Do NOT invent device details,
   causes, injuries, or outcomes.
2. If a field cannot be supported by the text, set it to null (JSON null).
3. Distinguish carefully:
   - failure_mode: abnormal behavior or failure of the device/system.
   - cause: stated or clearly implied mechanism/reason (not guesswork).
   - effect: what happened to the patient, user, or therapy as a result.
4. outcome_classification MUST be one of: malfunction, injury, death, other, unknown
   - malfunction: device issue without stated patient harm.
   - injury: narrative states harm, adverse clinical outcome, or hospitalization due to the event.
   - death: narrative states patient death linked to the event.
   - other: serious unclassified outcome explicitly described.
   - unknown: insufficient information to classify.
5. confidence_score: your calibrated confidence 0.0–1.0 for the overall extraction quality given text clarity.
6. normalized_risk_phrase: a short, generic phrase (≤ 120 chars) summarizing the risk theme using only
   supported content. Prefer canonical wording (e.g. dose delivery issues → mention under-delivery if supported).

Respond with a single JSON object only. No markdown fences, no commentary."""

MAUDE_NLP_USER_TEMPLATE = """Extract structured fields from the following adverse event narrative.

NARRATIVE:
---
{narrative}
---

Return JSON with keys:
failure_mode, cause, effect, component, harm, outcome_classification, confidence_score, normalized_risk_phrase

Use null for any unsupported field."""


# --- Normalization: map paraphrases to canonical failure-mode style phrases (regex → canonical) ---

_CANONICAL_FAILURE_CLUSTERS: List[Tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"\b("
            r"failed\s+to\s+deliver\s+full\s+dose|incomplete\s+injection|partial\s+dose\s+delivered|"
            r"under[-\s]?dose|incomplete\s+dose|partial\s+infusion|therapy\s+interrupted\s+before\s+completion"
            r")\b",
            re.I,
        ),
        "incomplete dose delivery",
    ),
    (
        re.compile(
            r"\b(battery\s+depleted|unexpected\s+shutdown|powered?\s+off\s+during\s+use|loss\s+of\s+power)\b",
            re.I,
        ),
        "unexpected power loss during use",
    ),
    (
        re.compile(r"\b(lead\s+fracture|fractured\s+lead|broken\s+lead)\b", re.I),
        "lead fracture",
    ),
]


def canonicalize_failure_risk_phrase(
    failure_mode: Optional[str],
    normalized_risk_phrase: Optional[str],
) -> Optional[str]:
    """
    Map known paraphrase clusters to a canonical phrase for cross-event analytics.
    Preference: match on failure_mode first, then normalized_risk_phrase from the LLM.
    """
    for text in (failure_mode, normalized_risk_phrase):
        if not text:
            continue
        low = text.lower()
        for pattern, canonical in _CANONICAL_FAILURE_CLUSTERS:
            if pattern.search(low):
                return canonical
    return normalized_risk_phrase


def _coerce_outcome(raw: Optional[str]) -> str:
    if not raw:
        return "unknown"
    s = str(raw).strip().lower()
    if s in ALLOWED_OUTCOMES:
        return s
    if "death" in s or "fatal" in s:
        return "death"
    if "injury" in s or "hospital" in s or "harm" in s:
        return "injury"
    if "malf" in s or "failure" in s:
        return "malfunction"
    return "other"


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Best-effort JSON object recovery from model output."""
    text = (text or "").strip()
    if not text:
        return {}
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            obj = json.loads(m.group(0))
            return obj if isinstance(obj, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def parse_llm_extraction(raw_content: str) -> Tuple[MaudeNarrativeLlmExtract, Dict[str, Any]]:
    """
    Parse model output into Pydantic. Never raises — returns low-confidence empty extract on failure.
    """
    data = _extract_json_object(raw_content)
    if not data:
        return (
            MaudeNarrativeLlmExtract(confidence_score=0.0, outcome_classification="unknown"),
            data,
        )
    try:
        model = MaudeNarrativeLlmExtract.model_validate(data)
    except Exception as e:
        logger.warning("LLM extraction parse failed; using empty extract: %s", e)
        model = MaudeNarrativeLlmExtract(
            confidence_score=0.0,
            outcome_classification="unknown",
        )
        return model, data

    if not any(
        [
            model.failure_mode,
            model.cause,
            model.effect,
            model.component,
            model.harm,
            model.normalized_risk_phrase,
        ]
    ):
        model = model.model_copy(
            update={
                "confidence_score": 0.0 if model.confidence_score is None else min(model.confidence_score, 0.35),
                "outcome_classification": model.outcome_classification or "unknown",
            }
        )

    oc = _coerce_outcome(model.outcome_classification)
    conf = model.confidence_score if model.confidence_score is not None else 0.5
    conf = max(0.0, min(1.0, float(conf)))
    model = model.model_copy(
        update={
            "outcome_classification": oc,
            "confidence_score": conf,
        }
    )
    canonical = canonicalize_failure_risk_phrase(model.failure_mode, model.normalized_risk_phrase)
    if canonical:
        model = model.model_copy(update={"normalized_risk_phrase": canonical})
    return model, data


class OpenAITransientError(Exception):
    """Retryable OpenAI / network failure."""


@retry(
    reraise=True,
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(OpenAITransientError),
)
def _is_transient_openai_error(exc: BaseException) -> bool:
    err = str(exc).lower()
    if "429" in err or "503" in err or "502" in err or "timeout" in err or "rate" in err or "connection" in err:
        return True
    code = getattr(exc, "status_code", None)
    return code in (429, 500, 502, 503)


def _call_openai_json(
    *,
    system_prompt: str,
    user_prompt: str,
) -> str:
    api_key = (os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    import openai

    client = openai.OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        if _is_transient_openai_error(e):
            logger.warning("OpenAI transient error; retrying: %s", e)
            raise OpenAITransientError(str(e)) from e
        logger.info("OpenAI json_object path failed (%s); retrying without response_format", e)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e2:
            if _is_transient_openai_error(e2):
                raise OpenAITransientError(str(e2)) from e2
            logger.exception("OpenAI call failed")
            raise RuntimeError(f"OpenAI extraction failed: {e2}") from e2


def run_llm_on_narrative(narrative: str) -> Tuple[MaudeNarrativeLlmExtract, str, Dict[str, Any]]:
    """Returns (parsed_extract, raw_content, raw_json_dict_for_audit)."""
    user_prompt = MAUDE_NLP_USER_TEMPLATE.format(narrative=narrative[:32000])
    raw = _call_openai_json(system_prompt=MAUDE_NLP_SYSTEM_PROMPT, user_prompt=user_prompt)
    parsed, raw_dict = parse_llm_extraction(raw)
    return parsed, raw, raw_dict


def extract_single_maude_event(db: Session, event_id: str) -> EventExtractResult:
    event = db.query(MaudeAdverseEvent).filter(MaudeAdverseEvent.id == event_id).first()
    if not event:
        return EventExtractResult(event_id=event_id, status="not_found", detail="MAUDE event not found")

    narrative = (event.narrative_text or "").strip()
    if not narrative:
        return EventExtractResult(
            event_id=event_id,
            status="skipped_no_narrative",
            detail="No narrative_text on record",
        )

    try:
        parsed, raw_content, raw_dict = run_llm_on_narrative(narrative)
    except Exception as e:
        logger.exception("Extraction failed for event %s", event_id)
        return EventExtractResult(event_id=event_id, status="error", detail=str(e)[:500])

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    fields = {
        "failure_mode": parsed.failure_mode,
        "cause": parsed.cause,
        "effect": parsed.effect,
        "component": parsed.component,
        "harm": parsed.harm,
        "outcome_classification": parsed.outcome_classification,
        "confidence_score": parsed.confidence_score,
        "normalized_risk_phrase": parsed.normalized_risk_phrase,
        "llm_model": model_name,
        "raw_llm_response": {"parsed_input": raw_dict, "raw_content_preview": raw_content[:8000]},
    }

    try:
        row = nlp_crud.upsert_extraction(db, event_id, fields)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception("DB upsert failed for event %s", event_id)
        return EventExtractResult(
            event_id=event_id,
            status="error",
            detail=(f"database: {e}")[:500],
        )

    logger.info(
        "NLP extraction stored event_id=%s extraction_id=%s outcome=%s conf=%s",
        event_id,
        row.id,
        parsed.outcome_classification,
        parsed.confidence_score,
    )
    return EventExtractResult(event_id=event_id, status="ok", extraction_id=row.id)


def extract_maude_events_batch(db: Session, req: PostmarketExtractRequest) -> PostmarketExtractResponse:
    ids = req.resolved_event_ids()
    results: List[EventExtractResult] = []
    succeeded = failed = skipped = 0

    for eid in ids:
        res = extract_single_maude_event(db, eid)
        results.append(res)
        if res.status == "ok":
            succeeded += 1
        elif res.status in ("skipped_no_narrative", "not_found"):
            skipped += 1
        else:
            failed += 1

    return PostmarketExtractResponse(
        requested=len(ids),
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
        results=results,
    )
