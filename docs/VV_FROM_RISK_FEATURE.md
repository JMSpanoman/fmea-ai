# Generate V&V from Risk – MVP

## Overview

This feature generates **risk-based Verification and Validation (V&V) test logic** from an FMEA row or risk record. It connects: **risk → mitigation → verification → validation → traceability** and is aimed at medical device design controls.

## API

### Generate

- **Endpoint:** `POST /ai/vv/generate-from-risk`
- **Auth:** Requires authenticated user (Pro plan for `/ai` routers).
- **Request body:**

```json
{
  "component": "Infusion pump battery",
  "failure_mode": "Battery depletes during use",
  "effect": "Therapy interruption",
  "cause": "Unexpected high power draw",
  "severity": 4,
  "occurrence": 2,
  "detection": 3,
  "mitigation": "Low battery alarm"
}
```

- **Response:** Structured V&V (see example in main feature request).

### Save to project

- **Endpoint:** `POST /ai/vv/save-from-risk`
- **Request:** Same shape as generate response, plus `project_id`, optional `fmea_row_id`, optional `risk_item_id`.
- **Response:** `{ "id", "project_id", "created_at" }`.

## Backend

- **Prompt:** `ai_prompts/vv_from_risk_prompt.txt`
- **Router:** `fmea_backend/routers/ai_phase2.py` (routes under `/ai/vv/...`)
- **Schemas:** `fmea_backend/schemas/vv.py` (`VVFromRiskGenerateRequest`, `VVFromRiskGenerateResponse`, `VVFromRiskSaveRequest`)
- **Model:** `fmea_backend/models/generated_vv.py` (`GeneratedVVRecord`) – table `generated_vv_records`

## Frontend

- **Types:** `frontend/src/types.ts` (`VVFromRiskGenerateRequest`, `VVFromRiskGenerateResponse`, etc.)
- **API:** `frontend/src/services/vvFromRiskApi.ts` (`generateVVFromRisk`, `saveVVFromRisk`)
- **Modal:** `frontend/src/components/VV/GenerateVVModal.tsx` – shows result, Copy all, Save to project
- **Entry points:**
  - **Project FMEA:** Table action (Science icon) and grid card “Generate V&V” on each saved row
  - **Risk Item detail:** Header “Generate V&V” button

## How to test locally

1. **Backend:** Set `OPENAI_API_KEY`, start API (e.g. `uvicorn main:app --reload` from `fmea_backend`).
2. **Frontend:** `npm run dev` from `frontend`.
3. **Pro user:** Log in as a user with `plan: "pro"` (e.g. dev-login with an email that gets Pro).
4. **FMEA:** Open a project → FMEA → ensure there are saved rows → Table: click Science on a row, or Grid: click “Generate V&V” on a card.
5. **Risk item:** Open a project → Risk Items → open one → click “Generate V&V” in the header.
6. In the modal: check sections, use “Copy all”, and if desired “Save to project”.

## Sample user flow

1. User opens **Project FMEA** and has saved rows (e.g. from Seed starter rows).
2. User clicks the **Science (V&V)** icon on one row (or “Generate V&V” in grid).
3. Modal opens; after a short loading state, generated V&V appears (verification test name, objective, method, validation scenario, acceptance criteria, calculations, worst-case conditions, traceability).
4. User clicks **Copy all** and pastes into a protocol or document.
5. User clicks **Save to project** to store the generated V&V in the project for traceability.
6. User closes the modal and can repeat for another row or navigate away.

## Extending later

- **Traceability matrix:** Link `GeneratedVVRecord` to design outputs / test protocols.
- **Protocol generation:** Use saved records to build full V&V protocol documents.
- **Risk-based rigor:** Prompt already scales acceptance criteria and worst-case by RPN/severity; further tuning is in `vv_from_risk_prompt.txt`.
