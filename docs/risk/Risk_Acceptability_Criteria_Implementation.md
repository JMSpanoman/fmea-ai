# Risk Acceptability Criteria — Implementation Summary

## Overview

The Risk Acceptability Criteria document generation has been upgraded to produce a complete, audit-ready, ISO 14971–aligned report with three-tier data precedence (project-approved → org default → system draft), source labels, gap detection, and optional AI-assisted narrative.

---

## 1. Implementation Plan (Completed)

1. **Schema & models** — Added `RiskAcceptabilityCriteria`, `OrganizationRiskCriteriaConfig`, `ProjectRiskCriteriaOverride`; migration SQL for all three tables.
2. **Service layer** — `risk_acceptability_criteria_service`: merge tiers, build full report (19 sections), gap detection; deterministic generation; AI only for clearly marked narrative when enabled.
3. **Renderer** — `risk_acceptability_criteria_renderer`: report dict → HTML with section badges (Approved / Org default / Draft / Needs review) and Required Manual Review list.
4. **Document control** — On Generate for document type `risk_acceptability_criteria`, build report, render HTML, persist to `RiskAcceptabilityCriteria` and update document content.
5. **API** — GET/POST report, GET merged criteria, GET/PATCH project override, GET/PATCH org config.
6. **Frontend** — Risk Acceptability Criteria page: load report, show HTML + manual review items, “Generate new version” button; Docs panel link “Open Risk Acceptability Report”.
7. **Seed & tests** — Seed script for default org config; tests for merge (no config → system_draft), gap detection, and report structure.

---

## 2. Changed / New Files

| Area | Files |
|------|--------|
| **Backend models** | `fmea_backend/models/risk_acceptability_criteria.py` (new), `fmea_backend/models/__init__.py` |
| **Migration** | `fmea_backend/migrations/add_risk_acceptability_criteria_tables.sql` |
| **Service** | `fmea_backend/services/risk_acceptability_criteria_service.py` (new) |
| **Renderer** | `fmea_backend/business_logic/risk_acceptability_criteria_renderer.py` (new) |
| **API** | `fmea_backend/routers/risk_acceptability_criteria_api.py` (new) |
| **Document control** | `fmea_backend/routers/document_control.py` (branch for `risk_acceptability_criteria`) |
| **App** | `fmea_backend/main.py` (model registration, router include) |
| **Prompt** | `ai_prompts/risk_acceptability_criteria_narrative.txt` (new, for future AI narrative) |
| **Frontend API** | `frontend/src/services/riskAcceptabilityCriteriaApi.ts` (new) |
| **Frontend page** | `frontend/src/pages/RiskAcceptabilityCriteriaPage.tsx` (new) |
| **Frontend routes/docs** | `frontend/src/App.tsx`, `frontend/src/features/docs/docsRegistry.ts`, `frontend/src/features/docs/DocDetailPanel.tsx` |
| **Tests** | `fmea_backend/tests/test_risk_acceptability_criteria.py` (new) |
| **Seed** | `fmea_backend/scripts/seed_risk_acceptability_org_config.py` (new) |

---

## 3. Sample Generated JSON (excerpt)

```json
{
  "document_header": {
    "document_title": "Risk Acceptability Criteria",
    "project_name": "Pacemaker Example",
    "project_id": "proj-uuid",
    "device_name": "Implantable cardiac pacemaker",
    "intended_use": "[Not set — complete in project profile]",
    "status": "draft",
    "version": 1,
    "date_generated": "2025-02-05T12:00:00.000000+00:00",
    "author_source": "SYSTEM-GENERATED DRAFT",
    "reviewer_placeholder": "[To be assigned]",
    "approver_placeholder": "[To be assigned]",
    "source_type": "placeholder"
  },
  "purpose": {
    "text": "This document defines how risks are classified as acceptable, conditionally acceptable (ALARP), or unacceptable, and how those criteria are used during initial and residual risk evaluation in accordance with ISO 14971.",
    "source_type": "system_draft"
  },
  "severity_scale": {
    "scale": [
      { "level": 1, "label": "Negligible", "definition": "No injury or negligible; no medical intervention." },
      { "level": 2, "label": "Minor", "definition": "Minor temporary injury; reversible; first aid or minimal intervention." },
      { "level": 3, "label": "Serious", "definition": "Serious injury or medical intervention required; may be reversible." },
      { "level": 4, "label": "Critical", "definition": "Life-threatening injury; permanent impairment; urgent intervention." },
      { "level": 5, "label": "Death", "definition": "Death or catastrophic harm." }
    ],
    "source_type": "system_draft",
    "label": "Default draft values — replace with organization-approved scale if different."
  },
  "risk_matrix": {
    "matrix": [
      ["Acceptable", "Acceptable", "Acceptable", "ALARP", "ALARP"],
      ["Acceptable", "Acceptable", "ALARP", "ALARP", "Unacceptable"],
      ["Acceptable", "ALARP", "ALARP", "Unacceptable", "Unacceptable"],
      ["ALARP", "ALARP", "Unacceptable", "Unacceptable", "Unacceptable"],
      ["ALARP", "Unacceptable", "Unacceptable", "Unacceptable", "Unacceptable"]
    ],
    "source_type": "system_draft",
    "label": "System-proposed draft matrix for team review. Do not use as official policy until approved."
  },
  "manual_review_items": [
    { "id": "severity_scale", "message": "Approved severity scale not configured.", "section": "Severity scale" },
    { "id": "probability_scale", "message": "Approved probability scale not configured.", "section": "Probability scale" },
    { "id": "risk_matrix", "message": "Official risk matrix not defined. Using system-proposed draft for team review.", "section": "Risk acceptability matrix" },
    { "id": "approver", "message": "Approver not assigned. Assign in Review and Approval section.", "section": "Review and approval" }
  ],
  "source_metadata": {
    "severity_scale": "system_draft",
    "probability_scale": "system_draft",
    "risk_matrix": "system_draft",
    "decision_rules": "system_draft"
  }
}
```

---

## 4. Sample Rendered Document Section (HTML excerpt)

```html
<h1>Risk Acceptability Criteria</h1>
<div class="meta">
  <p><strong>Project:</strong> Pacemaker Example | <strong>Project ID:</strong> proj-uuid</p>
  <p><strong>Device:</strong> Implantable cardiac pacemaker</p>
  <p><strong>Intended use:</strong> [Not set — complete in project profile]</p>
  <p><strong>Date generated:</strong> 2025-02-05T12:00:00.000000+00:00</p>
  <p><strong>Author/source:</strong> SYSTEM-GENERATED DRAFT</p>
</div>

<div class="section">
  <h2>5. Severity scale <span class="badge-draft">Draft</span></h2>
  <table class="rac-table">
    <thead><tr><th>Level</th><th>Label</th><th>Definition</th></tr></thead>
    <tbody>
      <tr><td>1</td><td>Negligible</td><td>No injury or negligible; no medical intervention.</td></tr>
      <tr><td>2</td><td>Minor</td><td>Minor temporary injury; reversible; first aid or minimal intervention.</td></tr>
      ...
    </tbody>
  </table>
</div>

<div class="manual-review">
  <h2>17. Required manual review items</h2>
  <ul>
    <li><strong>Severity scale:</strong> Approved severity scale not configured.</li>
    <li><strong>Probability scale:</strong> Approved probability scale not configured.</li>
    ...
  </ul>
</div>
```

---

## 5. How AI Fills Gaps Safely

- **Deterministic first** — Severity/probability scales, matrix, decision rules, residual risk rules, benefit–risk triggers, and transparency text are generated from code (system draft or org/project config). No freeform AI for thresholds.
- **AI only when requested** — If `include_ai_narrative` (e.g. “use_ai” option) is true, AI can draft narrative for purpose/scope/benefit–risk triggers using the template in `ai_prompts/risk_acceptability_criteria_narrative.txt`. All such content is labeled `source_type: "ai_generated"` and must be reviewed.
- **No invented policy** — The system never presents system or AI draft values as “approved” or “official”. Labels (Draft, Org default, Approved) and the “Required manual review items” section make gaps and source of each section explicit.
- **Regeneration** — Generating a new version creates a new `RiskAcceptabilityCriteria` row and updates the document content. Approved project overrides (stored in `ProjectRiskCriteriaOverride`) are not overwritten; they are merged again on each build.
- **No TBD** — Placeholders use guided text (e.g. “Complete in project profile”, “To be assigned by project lead”) so the document stays professional and audit-ready.

**Gap detection (Required manual review items):** Severity scale not configured; probability scale not configured; official risk matrix not defined; device description/intended use missing; approver not assigned; no linked Residual Risk Evaluation document.

---

## 6. Migration Steps

1. **Run SQL migration** (if not using `Base.metadata.create_all`):
   ```bash
   sqlite3 your.db < fmea_backend/migrations/add_risk_acceptability_criteria_tables.sql
   ```
   For PostgreSQL, run the equivalent DDL (adjust types if needed).

2. **Optional: seed org default** so reports can use org-level defaults:
   ```bash
   cd fmea_backend && python scripts/seed_risk_acceptability_org_config.py
   ```

3. **Restart backend** so new models and routes are loaded.

---

## 7. Assumptions

- No `Organization` model: a single “default” org config row is used; multi-tenant org IDs can be added later.
- Document content for Risk Acceptability Criteria is stored as HTML in the document record; full structured JSON is in `risk_acceptability_criteria.content_json`.
- Approver/approved_by are placeholders until an approval workflow is implemented; gap detection still flags “Approver not assigned”.
- Frontend “Edit criteria” (project override) uses the existing PATCH override API; a dedicated admin UI for override/org config can be added later.
