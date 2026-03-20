# Risk Acceptability Rule Engine

Deterministic, auditable classification for **project FMEA rows** (initial and residual risk).  
Aligned with ISO 14971-style workflows: classifications come from **versioned project criteria** stored in the database, not from AI.

## Concepts

| Piece | Role |
|--------|------|
| **ProjectRiskCriteria** (`project_risk_criteria`) | Versioned JSON config: severity/probability scales, 4×4 (or N×M) matrix, optional score thresholds, `special_rules` for keyword and policy rules. |
| **Rule engine** (`services/risk_rule_engine.py`) | Maps FMEA S/O (and D for score/hybrid) → matrix cell → `Acceptable` / `ALARP` / `Unacceptable`, then applies overrides. |
| **FMEARow** extensions | Persists classifications, flags (`benefit_risk_required`, `critical_function_flag`, `critical_hazard_category_flag`, `system_level_verification_required`, `approval_blocked`, `acceptable_for_release`), attestations (release, critical hazard, verification, structured benefit–risk `bra_*` fields), and `rule_engine_result_json`. |
| **RuleEvaluationAudit** | One row per evaluation run: inputs, matched rules, outputs, decision path text. |

## Evaluation methods

1. **matrix** (default) — Map FMEA numeric S/O into matrix band indices (configurable via `score_thresholds.fmea_severity_to_matrix_index` / `fmea_occurrence_to_matrix_index`), then lookup `risk_matrix[si][pi]`.
2. **score** — RPN = S×O×D (detection defaults to 1 if missing); compare to `acceptable_max_rpn` / `alarp_max_rpn`.
3. **hybrid** — Conservative merge: `max(matrix, score)` by severity order Acceptable < ALARP < Unacceptable.

## Special rules (data-driven)

`special_rules` holds:

- `critical_function_keywords`, `essential_function_keywords`, etc. — **lists only**, no hardcoded hazard strings in Python logic.
- `critical_hazard_category_keywords` + `critical_hazard_policies` — life-sustaining implant critical hazards: matrix severity floor, system-level verification, justification if not eliminated (see section below).
- `mandatory_policies` — release gating (death-severity B–R approval, residual review, etc.).
- `residual_acceptability_policies` — residual-only Acceptable / ALARP / Unacceptable rationale, ALARP attestations, formal release (see section below).
- `benefit_risk_workflow_policy` — structured B–R **documentation** (clinical benefit, benefit vs residual risk, state of the art, supporting evidence) and **multi-party acceptance** (Clinical/Medical, Quality/Regulatory, Design authority). Default `apply_when: formal_bra_required` aligns with the death-severity formal pathway; `enabled: false` restores legacy single `benefit_risk_formal_approval_recorded` only.
- `device_context` — e.g. `{ "life_sustaining": true }` for conditional rules.
- `rules[]` — declarative items with `id`, `type`, `condition`, optional `value`.

Supported rule `type` values include:

- `benefit_risk_required`
- `reviewer_justification_required`
- `min_classification` (floor, e.g. force at least `ALARP`)
- `set_critical_function_flag`
- `approval_blocked` (policy block)

Conditions support `severity_matrix_gte`, `residual_severity_matrix_gte`, `text_matches_any` (keyword list name or inline list), `device_context_equals`, and nested `all` / `any`.

## Built-in policies (always on)

Documented in `decision_path` for auditors:

- Highest severity band (S4) ⇒ benefit–risk review.
- Residual serious band (S3+) ⇒ reviewer justification required; missing text blocks release.
- `Unacceptable` ⇒ not acceptable for release unless the row attests **additional controls reduced risk** or **benefit–risk analysis approved** (see FMEA row boolean fields).

## Mandatory release policies (`special_rules.mandatory_policies`)

Defaults (overridable per project; thresholds are **FMEA numeric severities**, not matrix band indices):

| Rule | Default | Effect |
|------|---------|--------|
| Death / catastrophic pathway | `death_minimum_fmea_severity: 5` | When **initial** `severity` ≥ threshold: triggers structured benefit–risk workflow (see below) or legacy `benefit_risk_formal_approval_recorded`, regardless of probability. |
| Residual high severity | `residual_review_minimum_fmea_severity: 4` | When **residual** `residual_severity` ≥ threshold: documented justification, cross-functional review (`cross_functional_review_completed`), and formal release approval (`formal_release_approval_recorded`). |
| Disciplines (informational) | `release_review_disciplines` | Listed in `decision_path` (e.g. Engineering, Clinical, Quality). |

Engine outputs include `acceptable_for_release`, `release_status`, and `release_blockers`. `approval_blocked` is true when any release blocker is present. Persisted on the row: `acceptable_for_release` is recomputed from stored `rule_engine_result_json` when evaluations run.

## Structured benefit–risk workflow (`special_rules.benefit_risk_workflow_policy`)

When active (default: same trigger as formal B–R / death-severity pathway, `apply_when: formal_bra_required`), the analysis shall be **attested** as covering:

1. Description of clinical benefit — `bra_clinical_benefit_documented`
2. Comparison of benefit vs residual risk — `bra_benefit_vs_residual_risk_documented`
3. Consideration of state of the art — `bra_state_of_the_art_documented`
4. Supporting clinical or literature evidence (where available) — `bra_supporting_evidence_addressed`

**Acceptance** requires recorded approval from:

- Clinical/Medical — `bra_approval_clinical_medical_recorded`
- Quality/Regulatory — `bra_approval_quality_regulatory_recorded`
- Design authority (per project governance) — `bra_approval_design_authority_recorded`

Labels and required section IDs are configurable in criteria JSON; only known IDs map to these columns. Set `enabled: false` to require only the legacy single flag `benefit_risk_formal_approval_recorded`. With `use_multi_party_approval: false` (workflow still enabled), documentation gates still apply; use `enabled: false` for full legacy behavior.

Engine outputs: `benefit_risk_structured_workflow_active`, `benefit_risk_documentation_gates_active`, `benefit_risk_multi_party_approval_required`.

## Residual acceptability (`special_rules.residual_acceptability_policies`)

For **`evaluation_type: residual`** only (ISO 14971-oriented workflow after risk controls):

| Residual classification | Default policy |
|-------------------------|----------------|
| **Acceptable** | Documented rationale required (`reviewer_justification`). |
| **ALARP** | Documented justification + row attestations `residual_all_feasible_controls_implemented` and `residual_further_reduction_not_practicable` + **formal release approval** (`formal_release_approval_recorded`). |
| **Unacceptable** | Same release rules as initial: additional controls or approved benefit–risk; missing items → not acceptable for release. |

The engine adds a **decision_path** note that residual evaluation assumes applicable controls are implemented. Set `enabled: false` on `residual_acceptability_policies` to disable. Defaults apply when the key is omitted.

## Overall (aggregate) residual risk acceptability (`special_rules.global_residual_acceptability_policy`)

For **product-level** conclusions aligned with ISO 14971, the **global residual risk summary** includes `global_residual_acceptability` computed from persisted FMEA rows plus **project-level attestations** on `ProjectProfile`:

| Gate | Meaning |
|------|---------|
| Residual classified | Every row has a recognized `residual_risk_classification` (residual evaluation has been run). |
| Unacceptable escape | No row remains **Unacceptable** without `benefit_risk_analysis_approved` or `additional_controls_reduced_risk`. |
| No release blockers | No row has `approval_blocked` (captures missing ALARP justification/approvals, B–R gaps, mandatory release policies, etc.). |
| Overall B–R profile | `ProjectProfile.overall_device_benefit_risk_profile_acceptable` is explicitly **true** (strict attestation). |
| RMR documentation | `ProjectProfile.rmr_overall_residual_risk_conclusion_documented` is explicitly **true** — the conclusion that overall residual risk is acceptable is documented in the **Risk Management Report**. |

Configure under `special_rules.global_residual_acceptability_policy` with `enabled: false` to skip (legacy / matrix-only seed). When **no** `ProjectRiskCriteria` exists, the API disables this aggregate gate and returns counts only. Defaults match the pacemaker template builder and `tests/fixtures/pacemaker_risk_criteria.json`.

## Critical hazard categories (implantable pacemaker template)

Default pacemaker criteria include **critical hazard** keywords (loss of pacing, incorrect pacing, failure to deliver therapy, battery depletion, lead failure/dislodgement, sensing failure, etc.) under `critical_hazard_category_keywords`, with `critical_hazard_policies` enabled. When matched:

- Severity is evaluated at **at least** the configured **matrix band** (default index `4` = S4 on the ISO-style 4-level scale) unless `critical_hazard_severity_floor_waived` is true **and** the waiver is documented in `reviewer_justification`.
- **System-level verification** is required (`system_level_verification_recorded` on the row).
- **Documented justification** is required when the risk is **not** attested as eliminated (`risk_eliminated`).

## API (Pro)

Base path pattern: `/projects/{project_id}/…`

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/risk-criteria` | List criteria versions |
| POST | `/risk-criteria` | Create draft version |
| POST | `/risk-criteria/seed` | Seed ISO + pacemaker template |
| PUT | `/risk-criteria/{criteria_id}` | Update draft |
| POST | `/risk-criteria/{criteria_id}/approve` | Approve (validates full matrix first; archives prior approved) |
| POST | `/fmea/{fmea_row_id}/evaluate-initial` | Evaluate + persist + audit |
| POST | `/fmea/{fmea_row_id}/evaluate-residual` | Same for residual |
| POST | `/fmea/{fmea_row_id}/re-evaluate` | Both |
| POST | `/evaluate-all-risks` | Batch |
| GET | `/global-residual-risk-summary` | Aggregates from persisted row fields + `global_residual_acceptability` |
| GET | `/fmea/{fmea_row_id}/rule-audit` | Audit history |

Query param: `criteria_id` (optional) to pin a specific version; otherwise **latest approved**, else **latest any**.

## Frontend

- **Criteria UI:** `/projects/:projectId/risk-rule-criteria`
- **FMEA table:** badges, flags, expandable “Why?” panel, per-row re-run, batch “Evaluate all rows”.

## SQLite vs Postgres

- **SQLite:** `ensure_fmea_rule_engine_columns` adds new `fmea_rows` columns; `ensure_project_profile_governance_columns` adds RMF/RMR attestation columns on `project_profiles`; new tables via `create_all`.
- **Postgres:** apply `fmea_backend/migrations/add_project_risk_rule_engine.sql`, `add_fmea_mandatory_release_attestations.sql`, `add_fmea_critical_hazard_policy_columns.sql`, `add_fmea_residual_alarp_attestations.sql`, `add_fmea_benefit_risk_workflow_columns.sql`, and `add_project_profile_governance_attestations.sql` (or equivalent) if not using auto `create_all` in your environment.

## Tests

`pytest fmea_backend/tests/test_risk_rule_engine.py` — matrix, overrides, keywords, justification blocking, invalid config, hybrid, global summary, aggregate residual acceptability.
