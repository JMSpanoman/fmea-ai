# Post-market intelligence integration (Smart Risk)

End-to-end workflow: **openFDA MAUDE ingest → raw storage → NLP extraction → aggregation/scoring → APIs → `RealWorldEvidencePanel` → draft FMEA rows**.

## Assumptions

- **Pro plan**: All `/postmarket/*` routes use `require_pro` (same router dependency as before).
- **SQLite dev**: New `fmea_rows` columns and post-market tables are created via `Base.metadata.create_all` plus `ensure_fmea_postmarket_columns` for existing SQLite DBs.
- **PostgreSQL**: Run equivalent `ALTER TABLE fmea_rows ADD COLUMN ...` and rely on `create_all` for **new** tables (`postmarket_project_runs`, `postmarket_fmea_evidence_links`), or manage via your migration tool.
- **Determinism**: Synonym normalization is code-defined today; move mappings to DB per **IMPLEMENTATION_RULES** for admin editability.

## Backend file structure

| Path | Role |
|------|------|
| `fmea_backend/models/postmarket_intelligence.py` | `PostmarketProjectRun`, `PostmarketFmeaEvidenceLink` |
| `fmea_backend/models/fmea.py` | `evidence_source`, `postmarket_review_status`, `postmarket_evidence_summary` |
| `fmea_backend/crud/maude_adverse_event.py` | `list_event_ids_missing_extraction` |
| `fmea_backend/crud/postmarket_intelligence.py` | Persist pipeline runs + evidence links |
| `fmea_backend/crud/fmea.py` | Create/diff includes post-market columns |
| `fmea_backend/schemas/fmea.py` | FMEA create/update fields |
| `fmea_backend/schemas/postmarket_pipeline.py` | Pipeline, missing-risk report, add-to-FMEA schemas |
| `fmea_backend/schemas/postmarket_report.py` | Structured MAUDE report request/response |
| `fmea_backend/services/postmarket_report.py` | Report aggregation (`build_postmarket_report`) |
| `fmea_backend/services/postmarket_failure_mode_normalize.py` | Canonical failure-mode bucketing (extend / replace with embeddings) |
| `fmea_backend/services/postmarket_pipeline.py` | Orchestration |
| `fmea_backend/services/postmarket_match_service.py` | Matched vs unmatched + `build_missing_risks_for_project` |
| `fmea_backend/services/postmarket_fmea_bridge.py` | Draft FMEA row + evidence link |
| `fmea_backend/services/risk_scoring.py` | `device_type_override`, `resolve_device_type_for_postmarket`, canonical keys |
| `fmea_backend/routers/postmarket.py` | All post-market HTTP endpoints |
| `fmea_backend/db/runtime_migrations.py` | `ensure_fmea_postmarket_columns` (SQLite) |
| `fmea_backend/main.py` | Model import + migration hook |

## Frontend file structure

| Path | Role |
|------|------|
| `frontend/src/api/postmarketRiskScore.ts` | Typed clients: ingest, extract, pipeline, missing-risks, add-to-FMEA, scores |
| `frontend/src/components/postmarket/RealWorldEvidencePanel.tsx` | Pipeline UI, match report, default “Add to FMEA” API |
| `frontend/src/components/postmarket/PostMarketReport.tsx` | Full post-market report UI + charts |
| `frontend/src/components/postmarket/PostMarketReportSummaryCard.tsx` | Dashboard snapshot card |

## Example payloads

### `POST /postmarket/run-pipeline`

```json
{
  "project_id": "uuid",
  "device_type": "infusion pump",
  "device_name": null,
  "manufacturer_name": "Example Corp",
  "generic_device_type": null,
  "component": null,
  "failure_mode": null,
  "date_from": "2022-01-01",
  "date_to": "2025-01-01",
  "run_ingestion": true,
  "run_extraction": true,
  "run_scoring": true,
  "max_ingest_records": 400,
  "max_extract_events": 300
}
```

Response (abbreviated):

```json
{
  "records_fetched": 120,
  "records_inserted": 45,
  "records_skipped": 75,
  "records_extracted": 40,
  "extracted_failure_modes_count": 12,
  "scoring_summary": {
    "device_type_used": "infusion pump",
    "failure_mode_themes_scored": 18,
    "suggested_missing_count": 3
  },
  "top_missing_risks": [],
  "status": "partial",
  "warnings": ["NLP extraction failed for 2 event(s); check logs / API keys."],
  "disclaimer": "MAUDE/openFDA narratives are noisy…",
  "pipeline_run_id": "uuid"
}
```

### `GET /postmarket/missing-risks/{project_id}?device_type=infusion%20pump`

Returns `matched_themes`, `unmatched_themes`, `likely_missing_risks`, and `disclaimer`.

### `POST /postmarket/add-missing-risk-to-fmea`

```json
{
  "project_id": "uuid",
  "normalized_failure_mode": "incomplete dose delivery",
  "device_type": "infusion pump",
  "component": "pump mechanism",
  "suggested_effect": "Under-infusion",
  "suggested_cause": null,
  "source_event_ids": ["maude-event-uuid-1"]
}
```

Response:

```json
{
  "fmea_row_id": "uuid",
  "message": "Draft FMEA row created from post-market theme — expert review required before release use.",
  "disclaimer": "MAUDE-derived suggestions are not validated clinical hazards…"
}
```

## Post-market structured report (`POST /postmarket/report`)

**Assumption:** “Records analyzed” = rows with NLP extractions joined to MAUDE events (same filter stack as risk scoring). Ingested-but-not-extracted events are excluded from theme analytics.

Missing-risk and recommended-draft sections use `score_project_postmarket` with the **same** `date_from` / `date_to` / `component` / `failure_mode` filters as the rest of the report (aligned in `risk_scoring.score_project_postmarket` optional parameters).

### Example request

```json
{
  "project_id": "uuid",
  "device_type": "infusion pump",
  "device_name": "Acme Infuser X",
  "component": "battery",
  "failure_mode": null,
  "date_from": "2022-01-01",
  "date_to": "2025-03-01",
  "include_missing_risks": true,
  "include_trend_summary": true,
  "include_outcome_breakdown": true,
  "max_failure_modes": 10,
  "max_phrase_rows": 10
}
```

### Example response (abbreviated)

```json
{
  "report_title": "Post-Market Surveillance Summary (MAUDE)",
  "generated_at": "2025-03-24T12:00:00Z",
  "evidence_summary": {
    "total_maude_records_analyzed": 240,
    "qualitative_summary": "Analyzed 240 MAUDE-linked narrative extraction(s)..."
  },
  "top_failure_modes": [],
  "outcome_breakdown": [
    { "outcome": "malfunction", "count": 120, "percentage": 50.0 }
  ],
  "trend_summary": { "granularity": "monthly", "periods": [], "qualitative_summary": "..." },
  "missing_real_world_risks": [],
  "recommended_fmea_drafts": [],
  "disclaimer": "FDA MAUDE and openFDA extracts are incomplete..."
}
```

**Frontend:** `postPostmarketReport()` in `postmarketRiskScore.ts`; `PostMarketReport.tsx` for full page; `PostMarketReportSummaryCard.tsx` for dashboards (auto-fetches a lighter config with `max_failure_modes: 5`).

**PDF / print:** See comments in `schemas/postmarket_report.py` and `PostMarketReport.tsx` (`postmarket-report-root`, print CSS, or server-side PDF).

## Extension notes (future)

| Topic | Where to extend |
|-------|------------------|
| FDA recall data | New `source_system` on adverse-event–like table; reuse NLP schema with recall-specific prompts |
| Complaint system | Same extraction schema; `PostmarketFmeaEvidenceLink`-style link table with `complaint_id` |
| CAPA linkage | Nullable FK from evidence link or FMEA row metadata to `capas` |
| Trend alerts | Scheduled job reading `PostmarketProjectRun.scoring_summary` + thresholds in DB |
| Audit trail / version history | Versioned `PostmarketProjectRun`, `AuditLogEvent` on pipeline + FMEA draft creation |
| Embedding similarity | Replace or augment `canonicalize_failure_mode_key` + `_postmarket_covers_fmea` |

## Regulatory copy

All new API responses include or reference disclaimers: MAUDE is **not** incidence; expert review is **required** before changing FMEA. Draft rows use `postmarket_review_status=draft_expert_review`, `evidence_source=postmarket_maude`, `acceptable_for_release=False`, `approval_blocked=True`.
