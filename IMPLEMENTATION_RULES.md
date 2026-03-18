# Implementation Rules

These rules apply to backend, frontend, and shared design. Follow them for new features and when refactoring.

---

## 1. Use foreign keys and relational integrity

- **Backend**: Define and use proper foreign keys on all relational tables (e.g. `project_risk_items.device_id` → `devices.id`, `project_risk_items.component_id` → `components.id`). Rely on the database for referential integrity; avoid orphaned rows.
- **Migrations**: Add FKs in migrations; use `ON DELETE` / `ON UPDATE` where appropriate (e.g. CASCADE for owned children).
- **APIs**: Return stable IDs; do not rely on positional or name-based linking where an ID relationship exists.

---

## 2. Do not hardcode hazard text in the UI

- Hazard (and harm, control, verification) text must come from **data**: project risk items, hazard_library, harm_library, risk_control_library, verification_library, or user-entered fields (e.g. `hazard_text`, `harm_text`) stored per risk item.
- **Frontend**: No literal hazard strings in components (e.g. no "Electrical hazard", "Software failure" as constants). Use API responses and display `hazard_text` or library-derived labels.
- **Backend**: Report and table builders must use `_hazard_text(pri)`, `_harm_text(pri)`, library names, or stored text—never hardcoded fallbacks for real hazard names.

---

## 3. Make rules admin-editable

- Hazard generation rules, severity/probability mappings, acceptability thresholds, and similar **rules** must be stored in the database (or admin-configurable storage) and editable via admin/API, not only in code.
- Use tables such as `hazard_generation_rules`, lookup tables, or settings tables so non-developers can change behavior without code deploys.
- Prefer rule-driven logic (e.g. "if rule says use library X, use it") over if/else chains that encode business rules in application code.

---

## 4. Keep generation deterministic where possible

- When generating risk items, FMEA rows, hazard lists, or report sections from the same inputs (e.g. same device, same components, same rules), output should be **deterministic**: same input → same output.
- Avoid randomness in generation unless explicitly required (e.g. A/B tests). Seed any randomness when needed for reproducibility.
- Determinism supports auditing, regression testing, and traceability.

---

## 5. Preserve traceability across all accepted risk items

- Every accepted project risk item must be traceable: device → component → hazard → hazardous situation → harm → controls → verifications.
- **IDs**: Use and expose stable IDs (`project_risk_item.id`, `project_risk_control.id`, `project_verification.id`) so reports and exports can reference the same entities.
- **Reports and exports**: Link back to risk items and controls (e.g. include IDs or references) so that "this row in the report" maps to "this risk item" and its evidence.
- Do not drop or anonymize IDs in user-facing outputs when traceability is needed.

---

## 6. Support future AI enrichment but build rule-based functionality first

- Implement **rule-based** logic first (library lookups, templates, admin-editable rules). Use it as the default and the fallback.
- Design data models and APIs so that **AI enrichment** can be added later (e.g. optional fields for AI-suggested text, separate "source: rule | ai | user" or similar).
- Do not block core features on AI; ensure the app is usable and correct with rules and manual input only. AI should enhance, not replace, rule-based flows.

---

## 7. Build reusable services, not one-off pages

- **Backend**: Put business logic in **services** (e.g. `project_risk_outputs_service`, hazard/risk builders). Routers should be thin: auth, validation, call service, return response.
- **Frontend**: Reuse shared components (e.g. DataTable, TableExportBar, API clients). Prefer a single devices API and shared table/export patterns over duplicating logic per page.
- When adding a new report or export, extend existing services and reuse table-building helpers; avoid copy-pasting large blocks of logic into a single endpoint or page.

---

## 8. Design for scaling across multiple device types, not only pacemakers

- Avoid device-type-specific constants, labels, or workflows in core code (e.g. no "pacemaker" or "implantable" baked into shared services or DB schema).
- Use **generic** concepts: device, component, hazard, harm, control, verification. Device type (or category) should be a configurable attribute or classification, not a branch in core logic.
- Templates, rules, and libraries (hazard, harm, control, verification) should be reusable across device types; add device-type or product-line scoping only where the product explicitly requires it.

---

## Summary

| Principle | In practice |
|-----------|-------------|
| Foreign keys & integrity | FKs on all relations; migrations; no orphan rows. |
| No hardcoded hazard text | All hazard/harm/control text from DB or stored fields. |
| Admin-editable rules | Rules and thresholds in DB/admin, not only in code. |
| Deterministic generation | Same inputs → same outputs; no hidden randomness. |
| Traceability | Stable IDs; reports/exports link to risk items and evidence. |
| Rule-based first, AI later | Rule-based default; data model ready for AI enrichment. |
| Reusable services | Logic in services; thin routers; shared frontend components. |
| Multi–device type | Generic device/component/hazard model; no pacemaker-only logic in core. |
