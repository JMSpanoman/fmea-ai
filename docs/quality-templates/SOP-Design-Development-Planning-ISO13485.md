<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Section 7.3 (Design and development) — planning focus.
-->

# Design and Development Planning

---

## Title

**Design and Development Planning**

*Shorter public title (optional):* [D&D Planning]

---

## SOP Number

**[SOP-DDP-##]** *(align to [Company] numbering convention [WI-XXX])*

---

## Version

**[0.1]**

---

## Effective Date

**[YYYY-MM-DD]**

**Additional document control (for master list / eQMS index)**

| Field | Value |
|--------|--------|
| **Supersedes** | [None / prior SOP number and version] |
| **Document Owner** | [e.g., Director, Design Assurance / R&D] |
| **Planned review** | [Annual / when design control regulations or process change] |
| **Applicable standards** | ISO 13485:2016 (7.3); [ISO 14971:2019; IEC 60601-1, IEC 62304, IEC 62366-1; MDR/IVDR; 21 CFR 820.30 as applicable] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **planning, assigning, reviewing, and controlling** design and development (**D&D**) for **medical devices** and related **accessories** or **software**, so that D&D is **traceable**, conducted in **defined project stages** with **clear deliverables** and **review gates**, and **aligned** with **risk management** and **verification and validation (V&V)**, in accordance with **ISO 13485:2016, section 7.3**.

This SOP governs **D&D planning**; detailed activities for design **inputs, outputs, review, verification, validation, and transfer** are defined in **[SOP-###]** and recorded in the **Design History File (DHF)**. **Risk** activities follow **[SOP-Risk-###]** (ISO 14971).

---

## Scope

### In scope

- New product development, line extensions, major platform changes, and redesigns of **[product portfolio / project types — define]**.
- D&D from **concept** or **feasibility** through **design transfer** and handover to **[operations / post-market]**, as defined per project.
- **Software in a medical device** and **SaMD** where within scope of **[SOP-### / IEC 62304]**.

### Out of scope

- [Exploratory research with no design history file (DHF) intent — describe segregation in R&D policy, or *none*.]
- [Sustaining engineering changes that use only the change control process without a D&D project — cross-reference **[SOP-Change-###]**.]

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **Top management** | Resource approval at charter level; stage exit acceptance when required; alignment of D&D with QMS and management review. |
| **Project sponsor / product owner** | Business case, scope priority, escalation; market and regulatory strategy alignment. |
| **Project manager / D&D lead** | **Design plan** (§1); work assignment; scheduling of reviews; tracking of deliverables and open actions. |
| **Design Assurance / Quality** | QA participation in D&D; application of **risk, V&V, and DHF** procedures; notified body and audit support. |
| **Engineering** (as applicable) | Work packages, design outputs, and assigned V&V protocols and reports. |
| **Regulatory / Clinical (as applicable)** | Intended use and claims, regulatory path, clinical and usability inputs to the plan and reviews. |
| **Operations / Manufacturing** | Transfer readiness, pilot builds, and DHR linkages at defined stages. |

---

## Procedure

### 1. Design plan (required output)

1.1 For each D&D project or **product family** (as the Organization defines), the **D&D lead** shall establish a **design and development plan** (or equivalent **controlled** record) using **[eQMS / template DP-###]** before or at project kickoff. The design plan shall include at minimum:

- **Project identification** (name, code, device/UDI scope as applicable).
- **Objectives and success criteria** (technical, regulatory, schedule).
- **Referenced standards and regulations** (e.g. MDR, IVDR, FDA, IECs applicable to the device).
- **Project stages** (§2) with **entry/exit** criteria and **deliverables** (§4).
- **Roles and responsibilities** — **RACI** or matrix (§3).
- **Planned design reviews** (§5).
- **Interface to risk management** — RMP/RMF identifiers and review cadence (§7).
- **V&V strategy** — summary in the plan or pointer to a **V&V plan (VVP-###)** (§8).
- **Configuration / document control** for design data (DHF index, branching as needed) per **[SOP-DC-##]**.
- **Team training and competence** needs, linked to **[SOP-TR-##]**.

1.2 The design plan shall be **approved** by **[D&D director and Quality/Design Assurance — define]** and **updated** when scope, regulatory path, or risk profile **materially** changes (§6).

### 2. Project stages (typical)

*Tailor to device class and methodology (V-model, agile with regulated gates, etc.); document defaults in **[WI-###]**.*

| Stage (example) | Purpose (example) |
|-----------------|-------------------|
| **Charter / feasibility** | Business case, intended-use sketch, preliminary regulatory class |
| **Concept / architecture** | System architecture, initial hazards, IP and supplier screening |
| **Detailed design** | Design inputs and outputs, risk controls, specifications, software items per IEC 62304 |
| **V&V (build and test)** | Protocol execution, issue resolution, requirements trace |
| **Transfer / scale-up** | Process readiness, pilot, process risk (e.g. pFMEA), training to operations |
| **Release and sustaining handover** | Registration activities if in project scope, PMS hooks, D&D open-item closure |

2.1 **Stage gates** require DHF (or eDHF) **evidence** that **exit** criteria are met, or a **formal waiver** with **Quality** approval as defined in the design plan.

### 3. Responsibilities and assignment

3.1 A **RACI** (Responsible, Accountable, Consulted, Informed) or equivalent shall be in the design plan or **[linked document DOC-###]**.

3.2 One **accountable** owner per major work stream (e.g. software, electrical safety, human factors); the **D&D lead** remains accountable for overall plan integration.

3.3 **Outsourced** design and development shall be **identified** in the plan; supplier controls per **[SOP-Supplier-###]** and ISO 13485 **4.1** and **7.3** (as applicable) apply.

### 4. Deliverables (examples; authoritative list per project)

4.1 Typical **DHF** deliverables (non-exhaustive) include: user/ stakeholder needs; **design inputs** and **outputs**; **risk** file updates; **drawings and BOM**; **software** architecture and detailed design; **V&V** protocols and reports; D&D **review** records; **usability** engineering per IEC 62366-1 (if in scope); labeling/IFU drafts; **design transfer** package items; **DHF index** or completeness checklist per **[SOP-###]**.

4.2 **Placeholder** deliverables (e.g. “TBD V&V”) must be **closed** or **waived** before exiting a stage, except where the **design plan** explicitly allows iterative work (e.g. agile sprints) with a **defined** final verification/validation **gate**.

### 5. Design review points

5.1 Hold **D&D reviews** at minimum:

- (a) After design **inputs** are established/approved,  
- (b) When **design outputs** are ready and **before** design **verification** runs to completion,  
- (c) **Before** validation, clinical or usability work (if applicable) not yet covered,  
- (d) **Before** design **transfer** to manufacturing, and  
- (e) **Project closeout**  

— or **more** frequently as **stated in the design plan**.

5.2 Each review **record** in the **DHF** includes: **agenda**, **participants** (or e-sign), **objective** discussion of **inputs/outputs/risks** as appropriate, **decisions**, and **action items** with **owners** and **due** dates.

5.3 If **exit** criteria for a **stage** are not met, D&D does not advance until **rework** or an **updated design plan** is **approved** (§6).

### 6. Design change considerations

6.1 Changes to **scope**, **requirements**, **architecture**, or **hazard** profile shall update the **design plan**, **RMF** (or equivalent), and **V&V** and **trace** **impact** using **[CHG-### or template]**.

6.2 **Configuration and document** control of design **data** during D&D: **[SOP-DC-##]**; use **[PLM / version control / eQMS]** as defined for the project.

6.3 For **marketed** devices, changes are also governed by **[SOP-Change-###]**; a **D&D project** or work order may be **tied** to a **change** **number** and, where appropriate, a **condensed** design plan.

### 7. Linkage to risk management

7.1 The design plan shall reference the **RMP/RMF** (IDs or eQMS links). **Risk management reviews** (ISO 14971) shall align with project **stages** in §2 and when **hazards** or **controls** **change**—per **[SOP-Risk-###]**.

7.2 **Risk controls** and **residual risk** decisions shall **trace** to **design outputs** and to **V&V** in the **trace matrix** (§8).

### 8. Linkage to verification and validation (V&V)

8.1 The design plan and/or **V&V plan [VVP-###]** shall **summarize** or **reference** what is **verified** (design vs **design inputs**), what is **validated** (user needs, intended use, and/or clinical as applicable), **methods**, **acceptance criteria**, and any **independent** review per procedure.

8.2 **Execution** of V&V is per **[SOP-###]**. This planning SOP ensures V&V is **planned, resourced**, and **reflected** in **stage** exits and **deliverables** (§2, §4).

8.3 Device-specific **IEC 62304**, **62366-1**, **60601-1** (or other) V&V shall be **visible** in the V&V summary when in **scope** for the product.

### 9. Project closure and DHF

9.1 A project **closes** when the **design plan** and **DHF completeness** checklist (per applicable SOP) show: (a) required **reviews** and **action** items are **closed** or **waived**; (b) the **risk** file is **current** for the release being transferred; (c) **transfer** sign-off is **complete** if in scope; (d) D&D open issues are **closed** or assigned to **sustaining** with a target date.

9.2 **Retention** of D&D **records** per **[SOP-RC-##]** and the **DHF** index.

---

## Related Documents

| Document | Number |
|----------|--------|
| Design and development (inputs, outputs, review, V&V, transfer) | [SOP-###] |
| Risk management | [SOP-Risk-###] / ISO 14971 |
| Change control | [SOP-###] |
| Control of documents | [SOP-DC-##] |
| Control of quality records (DHF) | [SOP-RC-##] |
| Supplier control | [SOP-Supplier-###] |
| Training and competency | [SOP-TR-##] |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Design and development plan (per project) | D&D lead | [Per DHF / product and regulatory] | [eQMS / eDHF] |
| Review minutes, actions, and gate records | D&D / QA | [Per DHF] | [eDHF] |
| **Approved** revisions to design plan | D&D lead | [Per DHF] | [eQMS] |
| **RACI** or responsibility matrix (if not in plan) | D&D lead | [Per DHF] | [eQMS] |
| V&V plan (if separate from design plan) | D&D / QA | [Per DHF] | [eDHF] |

---

## Revision History

| Version | Date | Author | Description of change |
|---------|------|--------|------------------------|
| [0.1] | [YYYY-MM-DD] | [##] | Initial issue for review |
| | | | |

---

## Approval Signatures

*Obtain before **Effective Date**.*

| Role | Name | Signature | Date |
|------|------|------------|------|
| Prepared by | | | |
| Reviewed by (Design Assurance / Quality) | | | |
| Reviewed by (R&D / Engineering) | | | |
| Reviewed by (Regulatory, if applicable) | | | |
| Approved by (Management) | | | |

---

## Appendix A — ISO 13485:2016 mapping (informative)

| 13485:2016 | Expectation (summary) | This SOP |
|------------|------------------------|----------|
| 7.3.1 (planning) | D&D plan, stages, interfaces, reviews | §1, §2–5 |
| 7.3.2–7.3.5 | Design inputs, outputs, review, verification, validation (execution) | Referenced §5, §7, §8; **detail** in [SOP-###] |
| 7.3.6–7.3.7 | Design transfer, D&D file | §9, §2 last stage; **detail** in [SOP-###] |
| 7.1, 4.1 | Resource and risk application to design | §1, §7 |
| 4.2.4, 4.2.5 | Documented and retained evidence | [SOP-DC-##], [SOP-RC-##] |

---

## Appendix B (optional) — Audit checklist

- [ ] Design plan exists, approved, and matches project and device scope.
- [ ] Stages, **deliverables**, and **review** points are **defined** and **evidenced** in the DHF.
- [ ] RACI (or equivalent) current; outsourced D&D and suppliers identified and controlled.
- [ ] Design **changes** update the plan, **risk**, and V&V/trace as **needed**.
- [ ] Traceability to **RMF** and to **V&V** is **demonstrable** for the release.
- [ ] Project **closure** and **DHF completeness** before handover to **sustaining**.

---

*End of document*
