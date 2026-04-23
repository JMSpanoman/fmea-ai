"""
openFDA MAUDE (device adverse event) ingestion service.

Fetches device/event records from the public openFDA API, normalizes fields, and persists
with deduplication suitable for downstream risk analytics.

Extension hooks (future work):
- EXTENSION_POINT_FDA_RECALLS: Ingest FDA recall enforcement data (openFDA
  ``/drug/enforcement.json`` for drugs; device recalls often via
  ``https://api.fda.gov/device/recall.json`` or RSS / openFDA device recall endpoints
  as they evolve). Add a sibling module ``recall_ingestion.py`` and merge on UDI/DI
  or product code in a unified ``postmarket_events`` fact table or link table.
- EXTENSION_POINT_COMPLAINTS: Wire internal complaint modules (e.g. existing
  ``Complaint`` model), customer service exports, or MAUDE consumer submissions
  using the same normalization helpers and a ``source_system='internal_complaint'``
  discriminator.

Environment:
- ``OPENFDA_API_KEY`` — optional; increases rate limits for openFDA.
- ``OPENFDA_BASE_URL`` — default ``https://api.fda.gov``.
"""
from __future__ import annotations

import logging
import os
import re
import time
import unicodedata
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from crud import maude_adverse_event as maude_crud
from models.maude_adverse_event import MaudeAdverseEvent
from schemas.postmarket_maude import PostmarketIngestRequest, PostmarketIngestResponse

logger = logging.getLogger(__name__)

SOURCE_OPENFDA_MAUDE = "openfda_maude"
OPENFDA_DEVICE_EVENT_PATH = "/device/event.json"


class OpenFDAError(Exception):
    """Base error for openFDA client failures."""


class OpenFDARateLimitError(OpenFDAError):
    """HTTP 429 — caller may retry with backoff."""


class OpenFDABadResponseError(OpenFDAError):
    """Unexpected JSON shape or HTTP error."""


def normalize_text(value: Optional[str]) -> Optional[str]:
    """Lowercase, Unicode normalize, strip punctuation-heavy noise, collapse whitespace."""
    if value is None or not isinstance(value, str):
        return None
    s = unicodedata.normalize("NFKC", value).strip().lower()
    s = re.sub(r"[^\w\s\-./]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or None


def sanitize_openfda_query_term(term: str) -> str:
    """Remove Lucene-special characters that break openFDA ``search`` queries."""
    if not term:
        return ""
    s = unicodedata.normalize("NFKC", term)
    s = re.sub(r'[\"+\-&|!(){}[\]^~*?:\\/]', " ", s)
    return " ".join(s.split()).strip()


def collapse_device_label(brand: Optional[str], generic: Optional[str]) -> Optional[str]:
    """
    Merge brand + generic into one normalized label; dedupe identical tokens
    (lightweight substitute for fuzzy manufacturer-specific aliasing).
    """
    nb = normalize_text(brand)
    ng = normalize_text(generic)
    if nb and ng:
        if nb == ng:
            return nb
        seen: set[str] = set()
        out: List[str] = []
        for part in (nb, ng):
            for t in part.split():
                if t not in seen:
                    seen.add(t)
                    out.append(t)
        return " ".join(out)
    return nb or ng


def _parse_date_received(raw: Optional[str]) -> Optional[date]:
    if not raw or not isinstance(raw, str):
        return None
    digits = raw.strip()
    if len(digits) >= 8 and digits[:8].isdigit():
        try:
            return datetime.strptime(digits[:8], "%Y%m%d").date()
        except ValueError:
            return None
    return None


def _device_sequence(device: Dict[str, Any], fallback: int) -> int:
    raw = device.get("device_sequence_number")
    if raw is None or raw == "":
        return fallback
    try:
        return int(str(raw))
    except ValueError:
        return fallback


def _extract_narrative(result: Dict[str, Any]) -> Optional[str]:
    chunks: List[str] = []
    for block in result.get("mdr_text") or []:
        if isinstance(block, dict):
            t = block.get("text")
            if t:
                chunks.append(str(t).strip())
    probs = result.get("product_problem") or []
    if probs:
        chunks.append("Product problems: " + "; ".join(str(p) for p in probs))
    patient = result.get("patient") or []
    for p in patient:
        if isinstance(p, dict):
            pp = p.get("patient_problems") or []
            if pp:
                chunks.append("Patient problems: " + "; ".join(str(x) for x in pp))
    text = "\n\n".join(chunks).strip()
    if len(text) > 65000:
        text = text[:64997] + "..."
    return text or None


def _event_type(result: Dict[str, Any]) -> str:
    et = result.get("event_type")
    if et:
        return str(et)[:512]
    pp = result.get("product_problem") or []
    if pp:
        return str(pp[0])[:512]
    return "device_adverse_event"


def _manufacturer_from(device: Dict[str, Any], result: Dict[str, Any]) -> Optional[str]:
    m = device.get("manufacturer_d_name")
    if m:
        return str(m).strip() or None
    top = result.get("manufacturer")
    if isinstance(top, list) and top:
        return str(top[0]).strip() or None
    if isinstance(top, str) and top.strip():
        return top.strip()
    return None


# Injection / fluid-delivery vocabulary: broad OR matching for terms like "injector".
MAUDE_INJECTION_SYNONYMS: Tuple[str, ...] = (
    "injector",
    "syringe",
    "infusion",
    "pump",
    "pen",
)

# If any token matches or stems like these, expand to MAUDE_INJECTION_SYNONYMS (plus user tokens).
_INJECTION_STEMS = ("inject", "syring", "hypodermic", "subcutaneous", "bolus")


def expand_maude_device_terms(device_name: str) -> List[str]:
    """
    Map a user device hint to a bounded list of openFDA search tokens (OR’d later).
    Example: ``injector`` → injector + syringe + pen + infusion + pump + …
    """
    raw = sanitize_openfda_query_term(device_name)
    if not raw:
        raise ValueError("device_name is empty after sanitization")
    lower = raw.lower()
    tokens = re.findall(r"[a-z0-9]+(?:[-/][a-z0-9]+)?", lower)
    if not tokens:
        tokens = [lower]

    hit_injection_family = False
    for tok in tokens:
        if tok in MAUDE_INJECTION_SYNONYMS:
            hit_injection_family = True
            break
        if any(tok.startswith(s) for s in _INJECTION_STEMS):
            hit_injection_family = True
            break

    ordered: List[str] = []
    seen: set[str] = set()

    def add(w: str) -> None:
        w = sanitize_openfda_query_term(w).lower()
        if not w:
            return
        if w not in seen:
            seen.add(w)
            ordered.append(w)

    for t in tokens:
        add(t)
    if hit_injection_family:
        for s in MAUDE_INJECTION_SYNONYMS:
            add(s)
    return ordered[:14]


def _or_group_tokens(terms: List[str]) -> str:
    """
    Lucene parenthesized OR group, e.g. ``(a OR b)``.

    Use **spaces** around ``OR`` / ``AND`` / ``TO``. httpx encodes spaces as ``+`` in the
    query string; literal ``+`` in the string becomes ``%2B`` and openFDA/Lucene then see
    wrong tokens (404 / empty).
    """
    parts: List[str] = []
    seen: set[str] = set()
    for t in terms:
        for piece in re.split(r"[\s,;/]+", sanitize_openfda_query_term(t).lower()):
            if piece and piece not in seen:
                seen.add(piece)
                parts.append(piece)
    if not parts:
        raise ValueError("no device tokens for openFDA OR group")
    return "(" + " OR ".join(parts) + ")"


def _date_filter_clauses(req: PostmarketIngestRequest) -> List[str]:
    clauses: List[str] = []
    if req.date_from and req.date_to:
        df = req.date_from.strftime("%Y%m%d")
        dt = req.date_to.strftime("%Y%m%d")
        clauses.append(f"date_received:[{df} TO {dt}]")
    elif req.date_from:
        df = req.date_from.strftime("%Y%m%d")
        clauses.append(f"date_received:[{df} TO 30000101]")
    elif req.date_to:
        dt = req.date_to.strftime("%Y%m%d")
        clauses.append(f"date_received:[19000101 TO {dt}]")
    return clauses


def _optional_filter_clauses(req: PostmarketIngestRequest) -> List[str]:
    """Extra AND clauses (manufacturer, generic type)."""
    parts: List[str] = []
    if req.generic_device_type:
        gt = sanitize_openfda_query_term(req.generic_device_type)
        if gt:
            g = _or_group_tokens([gt])
            parts.append(
                f"(device.generic_name:{g} OR device.brand_name:{g} OR device.openfda.device_name:{g})"
            )
    if req.manufacturer_name:
        mn = sanitize_openfda_query_term(req.manufacturer_name)
        if mn:
            parts.append(f'device.manufacturer_d_name:"{mn}"')
    return parts


def device_match_clause_triple_field(terms: List[str]) -> str:
    """
    OR across openFDA-indexed device text fields (``device.device_name`` is not searchable).
    """
    g = _or_group_tokens(terms)
    return (
        f"(device.generic_name:{g} OR device.brand_name:{g} OR device.openfda.device_name:{g})"
    )


def device_match_clause_wildcard_stem(seed_term: str) -> str:
    """Fallback: substring wildcard on a short stem (e.g. ``inject`` from ``injector``)."""
    t = sanitize_openfda_query_term(seed_term).lower()
    if not t:
        t = "device"
    stem = t[:6] if len(t) >= 4 else t
    return (
        f"(device.generic_name:*{stem}* OR device.brand_name:*{stem}* "
        f"OR device.openfda.device_name:*{stem}*)"
    )


def build_openfda_search_strategies(req: PostmarketIngestRequest) -> List[Tuple[str, str]]:
    """
    Ordered strategies: try strictest first (optional filters), then drop filters / add wildcards.
    """
    expanded = expand_maude_device_terms(req.device_name)
    core = device_match_clause_triple_field(expanded)
    wild = device_match_clause_wildcard_stem(expanded[0])
    dates = _date_filter_clauses(req)
    optional = _optional_filter_clauses(req)

    strategies: List[Tuple[str, str]] = []

    def joinq(device_clause: str, extras: List[str]) -> str:
        parts = [device_clause] + extras + dates
        return " AND ".join(parts)

    strategies.append(("synonym_triple_field_optional_dates", joinq(core, optional)))
    strategies.append(("synonym_triple_field_dates_only", joinq(core, [])))
    strategies.append(("wildcard_stem_dates_only", joinq(wild, [])))
    strategies.append(("synonym_triple_field_no_date", core))
    strategies.append(("wildcard_stem_no_date", wild))
    return strategies


def build_openfda_search_query(req: PostmarketIngestRequest) -> str:
    """Backward-compatible: primary (strictest) openFDA search string."""
    return build_openfda_search_strategies(req)[0][1]


@retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=45),
    retry=retry_if_exception_type(OpenFDARateLimitError),
)
def _http_get_openfda(url: str, params: Dict[str, Any]) -> httpx.Response:
    with httpx.Client(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
        resp = client.get(url, params=params)
        if resp.status_code == 429:
            logger.warning("openFDA rate limit (429); retrying with backoff")
            raise OpenFDARateLimitError("rate limited")
        return resp


def fetch_openfda_page(
    *,
    base_url: str,
    search: str,
    skip: int,
    limit: int,
    api_key: Optional[str],
) -> Dict[str, Any]:
    """Fetch one page of device/event results. Raises on HTTP errors."""
    url = base_url.rstrip("/") + OPENFDA_DEVICE_EVENT_PATH
    params: Dict[str, Any] = {"search": search, "limit": limit, "skip": skip}
    if api_key:
        params["api_key"] = api_key

    try:
        resp = _http_get_openfda(url, params)
    except OpenFDARateLimitError:
        raise
    except httpx.HTTPError as e:
        logger.exception("openFDA HTTP failure: %s", e)
        raise OpenFDAError(f"HTTP error calling openFDA: {e}") from e

    if resp.status_code == 404:
        try:
            err_payload = resp.json()
            err = err_payload.get("error") if isinstance(err_payload, dict) else None
            if isinstance(err, dict) and err.get("code") == "NOT_FOUND":
                logger.info("openFDA 404 NOT_FOUND (empty query match); treating as zero results")
                return {"meta": {"results": {"total": 0}}, "results": []}
        except ValueError:
            pass

    if resp.status_code >= 400:
        body = resp.text[:500]
        logger.error("openFDA error %s: %s", resp.status_code, body)
        raise OpenFDAError(f"openFDA returned {resp.status_code}: {body}")

    try:
        return resp.json()
    except ValueError as e:
        logger.exception("openFDA malformed JSON")
        raise OpenFDABadResponseError("Malformed JSON from openFDA") from e


def _flatten_devices(result: Dict[str, Any]) -> List[Tuple[int, Dict[str, Any]]]:
    devices = result.get("device")
    if isinstance(devices, list) and devices:
        out: List[Tuple[int, Dict[str, Any]]] = []
        for i, d in enumerate(devices):
            if isinstance(d, dict):
                out.append((_device_sequence(d, i + 1), d))
        return out
    return [(0, {})]


def map_to_model(
    *,
    result: Dict[str, Any],
    device_seq: int,
    device: Dict[str, Any],
) -> Optional[MaudeAdverseEvent]:
    report_key = result.get("report_number") or result.get("safety_report_number")
    if not report_key:
        return None
    report_key = str(report_key).strip()
    if not report_key:
        return None

    brand = device.get("brand_name")
    generic = device.get("generic_name")
    brand_s = str(brand).strip() if brand else None
    generic_s = str(generic).strip() if generic else None

    mfr = _manufacturer_from(device, result)
    product_code = device.get("device_report_product_code")
    pc = str(product_code).strip() if product_code else None

    raw_payload = {
        "openfda_report": result,
        "device_sequence": device_seq,
        "device_record": device,
    }

    narrative = _extract_narrative(result)
    evt = _event_type(result)
    dr = _parse_date_received(result.get("date_received"))

    row = MaudeAdverseEvent(
        source_system=SOURCE_OPENFDA_MAUDE,
        source_report_key=report_key,
        device_sequence=device_seq,
        raw_record=raw_payload,
        normalized_device_name=collapse_device_label(brand_s, generic_s),
        event_type=evt,
        narrative_text=narrative,
        manufacturer=normalize_text(mfr) or mfr,
        brand_name=brand_s,
        generic_name=generic_s,
        date_received=dr,
        product_code=pc,
    )
    return row


def _probe_openfda_has_results(
    *,
    base_url: str,
    search: str,
    api_key: Optional[str],
) -> Tuple[bool, Optional[int]]:
    """First-page probe: returns (has_rows, meta_total)."""
    payload = fetch_openfda_page(base_url=base_url, search=search, skip=0, limit=1, api_key=api_key)
    meta = payload.get("meta") or {}
    results_meta = meta.get("results") or {}
    total = results_meta.get("total")
    total_i: Optional[int] = None
    if isinstance(total, int):
        total_i = total
    elif isinstance(total, str) and total.isdigit():
        total_i = int(total)
    results = payload.get("results")
    has = bool(results) and isinstance(results, list) and len(results) > 0
    if total_i is not None and total_i > 0:
        has = True
    return has, total_i


def ingest_openfda_maude(db: Session, req: PostmarketIngestRequest) -> PostmarketIngestResponse:
    """
    Run a bounded ingestion from openFDA into ``maude_adverse_events``.

    Returns counts for fetched (device rows examined), inserted, and skipped duplicates.
    """
    warnings: List[str] = []
    try:
        strategies = build_openfda_search_strategies(req)
        expanded_terms = expand_maude_device_terms(req.device_name)
    except ValueError as e:
        logger.warning("Invalid ingest request: %s", e)
        raise

    base_url = os.getenv("OPENFDA_BASE_URL", "https://api.fda.gov").strip()
    api_key = os.getenv("OPENFDA_API_KEY", "").strip() or None

    query_attempts: List[str] = []
    chosen_search: Optional[str] = None
    chosen_label: str = strategies[0][0]

    for label, search in strategies:
        entry = f"{label}: {search}"
        query_attempts.append(entry)
        logger.info("openFDA MAUDE probe strategy=%s full_query=%s", label, search)
        try:
            has_rows, probe_total = _probe_openfda_has_results(
                base_url=base_url, search=search, api_key=api_key
            )
        except OpenFDAError:
            raise
        logger.info(
            "openFDA MAUDE probe result strategy=%s has_rows=%s meta_total=%s",
            label,
            has_rows,
            probe_total,
        )
        if has_rows:
            chosen_search = search
            chosen_label = label
            break

    if chosen_search is None:
        chosen_search = strategies[-1][1]
        chosen_label = strategies[-1][0]
        warnings.append(
            "openFDA returned no rows on first-page probes; ran broadest fallback query — "
            "check optional filters (manufacturer / generic type / dates)."
        )

    search = chosen_search
    logger.info(
        "MAUDE ingest using strategy=%s final_openfda_query=%s max_records=%s page_size=%s",
        chosen_label,
        search,
        req.max_records,
        req.page_size,
    )

    fetched = 0
    inserted = 0
    skipped_duplicates = 0
    skipped_malformed = 0
    openfda_total_hint: Optional[int] = None
    sample_keys: List[str] = []

    skip = 0
    page_size = min(req.page_size, 1000)

    try:
        while fetched < req.max_records:
            try:
                payload = fetch_openfda_page(
                    base_url=base_url,
                    search=search,
                    skip=skip,
                    limit=page_size,
                    api_key=api_key,
                )
            except OpenFDAError as e:
                logger.error("openFDA fetch failed: %s", e)
                raise

            meta = payload.get("meta") or {}
            results_meta = meta.get("results") or {}
            if openfda_total_hint is None and isinstance(results_meta.get("total"), int):
                openfda_total_hint = results_meta["total"]

            results = payload.get("results")
            if not results:
                if skip == 0:
                    warnings.append("openFDA returned no results for the selected ingest query (empty result set).")
                logger.info("openFDA page empty at skip=%s query=%s", skip, search)
                break

            if not isinstance(results, list):
                logger.error("openFDA results is not a list")
                raise OpenFDABadResponseError("Unexpected openFDA payload: results not a list")

            for result in results:
                if fetched >= req.max_records:
                    break
                if not isinstance(result, dict):
                    skipped_malformed += 1
                    logger.warning("Skipping non-dict result row")
                    continue

                rk = result.get("report_number") or result.get("safety_report_number")
                if rk and len(sample_keys) < 8:
                    sample_keys.append(str(rk).strip())

                for device_seq, device in _flatten_devices(result):
                    if fetched >= req.max_records:
                        break
                    fetched += 1
                    try:
                        model = map_to_model(result=result, device_seq=device_seq, device=device)
                        if model is None:
                            skipped_malformed += 1
                            logger.warning("Skipping result without report_number")
                            continue

                        if maude_crud.exists_dedup_key(
                            db,
                            source_system=model.source_system,
                            source_report_key=model.source_report_key,
                            device_sequence=model.device_sequence,
                        ):
                            skipped_duplicates += 1
                            continue

                        maude_crud.insert_event(db, model)
                        inserted += 1
                    except Exception:
                        skipped_malformed += 1
                        logger.exception("Malformed or failed row during MAUDE ingest")

            if len(results) < page_size:
                break

            skip += page_size
            if not api_key:
                time.sleep(0.25)

        db.commit()
    except Exception:
        db.rollback()
        logger.exception("MAUDE ingest aborted; rolled back transaction")
        raise

    logger.info(
        "MAUDE ingest complete strategy=%s fetched=%s inserted=%s skipped_duplicates=%s "
        "skipped_malformed=%s openfda_total_hint=%s",
        chosen_label,
        fetched,
        inserted,
        skipped_duplicates,
        skipped_malformed,
        openfda_total_hint,
    )

    return PostmarketIngestResponse(
        fetched=fetched,
        inserted=inserted,
        skipped_duplicates=skipped_duplicates,
        skipped_malformed=skipped_malformed,
        openfda_total_hint=openfda_total_hint,
        warnings=warnings,
        search_query_used=search,
        query_attempts=query_attempts,
        expanded_device_terms=expanded_terms,
        sample_source_report_keys=sample_keys,
    )
