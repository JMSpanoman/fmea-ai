---
title: Risk Analysis Checklist
standard: ISO 14971-style
doc_type: risk_analysis_checklist
use_with: Risk_Analysis_Template.md
---

# Risk Analysis Checklist (ISO 14971-style)

Use this checklist to confirm audit readiness of a Risk Analysis document. Mark each item as Complete / N/A and record references.

## 1) Purpose & Scope

- [ ] **Purpose statement** is present and aligns with ISO 14971 intent.
- [ ] **Scope** clearly defines product boundaries and included/excluded configurations.
- [ ] **Lifecycle coverage** is stated (design/manufacturing/distribution/use/service/end-of-life as applicable).
- [ ] **Interfaces** (user/device/environment/external systems) are identified.
- [ ] **Related documents** are referenced (RMP, acceptability criteria, verification evidence).

## 2) Intended Use, Users, Use Environment

- [ ] Intended use is stated and consistent with product labeling/claims.
- [ ] Intended users are defined.
- [ ] Use environment is defined (including constraints relevant to safety).
- [ ] User/patient population is defined where applicable.
- [ ] Key safety characteristics are listed.

## 3) Foreseeable Misuse (top 5)

- [ ] Top 5 foreseeable misuse scenarios are documented.
- [ ] Misuse scenarios are plausible and linked to hazardous situations where applicable.
- [ ] Any assumptions/limitations are stated.

## 4) Risk Acceptability Framework + link to RMP

- [ ] Risk acceptability criteria are summarized (not just mentioned).
- [ ] RMP reference is included (document ID/location/link).
- [ ] Decision rules are explicit (acceptable vs unacceptable; escalation/approval requirements).

## 5) Hazard → Hazardous Situation → Harm mapping

- [ ] Hazard, hazardous situation, and harm are each defined (consistent terminology).
- [ ] Mapping table exists and includes IDs.
- [ ] Mapping covers normal use and foreseeable misuse where applicable.
- [ ] Traceability is maintained (IDs referenced in risk tables and controls).

## 6) Initial risk vs Residual risk separation

- [ ] Scoring assumptions are defined (S/P/D or risk matrix definitions).
- [ ] Initial (pre-control) and residual (post-control) risk are clearly separated.
- [ ] Each risk entry includes:
  - [ ] Hazard ID
  - [ ] Hazardous situation ID
  - [ ] Harm ID
  - [ ] Initial risk ratings
  - [ ] Risk control IDs
  - [ ] Residual risk ratings
  - [ ] Residual acceptability decision

## 7) Risk control details (hierarchy + rationale)

- [ ] Risk controls are documented with hierarchy:
  - [ ] Inherent safety by design
  - [ ] Protective measures (device/process)
  - [ ] Information for safety (labeling/IFU/training)
- [ ] Rationale is included for why each control is effective.
- [ ] Side effects / new hazards introduced by controls are assessed and recorded.
- [ ] Control-to-risk traceability is explicit (Risk IDs listed per control).

## 8) Verification of risk controls (method + evidence IDs + status)

- [ ] Verification method is specified for each control (test/inspection/analysis).
- [ ] Evidence identifiers are recorded (test IDs, report IDs, inspection records, etc.).
- [ ] Acceptance criteria are stated and objective.
- [ ] Status is recorded (Planned / Pass / Fail) with date and owner where applicable.

## 9) Residual Risk Summary + benefit–risk justification references

- [ ] Residual risk summary exists (highest residual risks identified).
- [ ] Overall conclusion on residual risk acceptability is recorded.
- [ ] For any residual risks requiring benefit–risk justification:
  - [ ] A benefit–risk reference is provided (document ID/link).
  - [ ] Decision/approval is recorded.

## 10) Production & Post-Production feedback hooks (PMS)

- [ ] PMS sources are defined (complaints, NC, CAPA, service, supplier, vigilance, literature, etc.).
- [ ] Review triggers are defined (quantitative thresholds or clear qualitative triggers).
- [ ] Responsibility and review cadence are stated or referenced.

## 11) Revision history + change summary

- [ ] Revision history table exists.
- [ ] Each revision has date, author, change summary, and approval (as required).

## System Integrity Checks (smartRisk)

- [ ] All residual risk evaluations are based on versioned, immutable risk records.
- [ ] No residual risk data is inferred or auto-generated without explicit entry.
- [ ] Report outputs accurately reflect available data (no silent assumptions).

---

## Open Items / TODO

If any items are incomplete due to missing context, list them here with an owner and target date.

- [ ] TODO: ____________________ (Owner: ________, Due: ________)
- [ ] TODO: ____________________ (Owner: ________, Due: ________)

