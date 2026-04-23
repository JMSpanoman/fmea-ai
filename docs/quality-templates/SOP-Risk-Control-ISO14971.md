<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 14971:2019 — risk control (Clause 7): options, implementation, V&V, RMF, residual risk.
  SOP number [SOP-R7-##] is a Clause 7 mnemonic; do not confuse with [SOP-RC-##] (record control in this document set).
  Cross-references: RMP, RMF, D&D, change, V&V, labeling, benefit–risk, residual risk, [SOP-RM-##].
-->

# Risk Control

---

## Title

**Risk Control (ISO 14971 — Clause 7)**

*Shorter public title (optional):* [RMF risk controls]

---

## SOP Number

**[SOP-R7-##]** *(Clause 7 risk control; align to [Company] numbering; do not reuse [SOP-RC-##] for record control in the same index without clear distinction)*

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
| **Document Owner** | [e.g., Director, Regulatory and Quality / Design assurance or risk lead] |
| **Planned review** | [Annual / when RMP, product line, or state of the art for controls changes] |
| **Applicable standards** | **ISO 14971:2019;** [ISO 13485:2016; IEC 60601, IEC 62304, IEC 62366-1, ISO 15223-1 as applicable; MDR, IVDR, 21 CFR 820 as applicable] |
| **Related SOPs** | [SOP-RM-## Risk management; SOP-RE-## Risk evaluation; SOP-RA-## Risk analysis; SOP-### Design and development; SOP-### Design change; SOP-### Verification/validation; SOP-### Labeling/IFU; SOP-RC-## Records; SOP-DC-## Documents] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **identifying, selecting, implementing, verifying, and documenting** **risk control measures** in accordance with **ISO 14971:2019, Clause 7,** the **risk management plan (RMP)**, and **[SOP-RM-##]**, and for **traceable** **evidence** in the **risk management file (RMF)**.

Controls shall be considered and applied in **priority order** per **Clause 7: (1)** **inherent safety** by **design, (2)** **protective measures** in the **device** or **manufacturing** **process, (3)** **information** for **safety** (including **labeling** and **IFU**). The **(3)** option is used **only** when **(1)** and **(2)** are **inadequate** or **impracticable** for **further** **risk** **reduction,** and must be **justified** and **verified** as **effective** in the **RMP/RMF**.

This SOP **links** **control** **option** **analysis,** **implementation** **tracking,** and **verification** to **design** **outputs,** **change** **records,** and **residual-** **risk** **re-evaluation** per the **RMP** and **[SOP-RM-##]**.

---

## Scope

### In scope

- **Risk** **control** for **[device / IVD / SaMD / product family — as applicable]** from **unacceptable** or **ALARP-** **bounded** **findings** through **post-** **market** **update** of **controls** as the **RMP** **requires**
- **Inherent** **safety,** **protective** **measures,** and **information** for **safety,** with **RMP-** **documented** **rationale** when **labeling/IFU** is a **control**
- **Control** **option** **analysis,** **implementation** **status,** **V&V** of **control** **effectiveness,** and **linkage** to **DCR/DHF** and **residual** **risk** in the **RMF**

### Out of scope

- **Non-**safety business or marketing-only **changes,** unless **D&D/change** **policy** or a **DCR** **brings** them under the **RMP** (if **none,** state **none**)
- **Regulatory** **submission** **strategy** without **RMP-** **linked** **safety** **objectives**

**Justification** for out-of-scope items: **[RMP, quality plan, or RMF index]**

---

## Responsibilities

| Role | Responsibility |
|------|------------------|
| **Risk** **management** **lead** | **RMP** **scope** for **controls;** **residual-** **risk** **and** **review** **readiness;** **RMF** **completeness** for **Clause** **7** |
| **Design** **&** **development** / **SMEs** | **Propose** **(1)–(3)** **measures,** **own** **design** **outputs,** and **V&V** **evidence** **per** **D&D** **plan** |
| **Operations** / **Mfg.** (as **applicable)** | **Process** **protective** **measures,** **DHR,** and **escalation** of **safety** **issues** |
| **Labeling** / **RA** (as **applicable)** | **IFU,** **warnings,** and **other** **information** for **safety** when a **control** **measure** |
| **RAQA** | **QMS** **linkage,** **records,** and **audit** **readiness** |
| **PMS** / **complaints** | **Post-** **market** **inputs** that **trigger** **control** **re-evaluation** per **RMP** / **[SOP-RM-##]** |

---

## Procedure

### 1. General: priority and RMP

- The RMP (per ISO 14971:2019 4.4) shall define how the (1)-(3) priority hierarchy is applied and how residual risk is re-evaluated after controls.
- Risk registers (e.g. FMEA) shall tag each risk control as (1) inherent safety by design, (2) protective measure, or (3) information for safety, and link to a unique reference (requirement ID, drawing, label ID, process parameter, etc.).
- Reliance on (3) alone without documented justification that (1) and (2) are inadequate or impracticable shall be escalated per the RMP.

### 2. Inherent safety by design (option 1)

- For each risk in scope, consider design changes that reduce or remove the hazard (materials, architecture, energy limits, fail-safe behavior, geometry, software safety architecture, etc.) before relying on (2) or (3).
- Document (1) in D&D outputs (requirements, design inputs/outputs) and in the RMF (or DHF cross-reference per RMP).

### 3. Protective measures (option 2)

- Define protective measures in the device (guards, interlocks, alarms) or manufacturing process (controls, inspection, process windows) that reduce residual risk from hazards not fully addressed by (1).
- Link (2) to released specifications, work instructions, DHR evidence, or validation protocols as applicable.

### 4. Information for safety (option 3)

- Use labeling, IFU, training content, or other information for safety as a control only when (1) and (2) do not reduce risk to the RMP level and when the RMP says (3) is appropriate.
- Information for safety must be accurate, visible to the intended user, and verified for effectiveness (e.g. usability validation, labeling review, comprehension testing as RMP-defined).
- Follow labeling, usability, and software SOPs and IEC 62366-1, IEC 62304, etc., as in scope.

### 5. Control option analysis

- For significant risks or per RMP-defined thresholds, record a brief option analysis: alternatives, trade-offs, (1)-(3) order, and rationale for the chosen combination.
- FMEA or eQMS (e.g. SmartRisk) rows may hold the text or link to a DCR or RMF attachment.

### 6. Implementation tracking

- Each control shall have an owner, target milestone, and status in the RMF or D&D plan (open, implemented, pending V&V).
- Change orders (DCR) or equivalent shall tie control implementation to released design or process revisions per the design change SOP [SOP-###].

### 7. Verification of control effectiveness

- For each control, define and execute verification or validation as the RMP and D&D plan require (design verification, process validation, software tests, usability, etc.).
- Re-estimate residual risk (or FMEA S/O, RPN, or bands) after controls and compare to RMP acceptability per [SOP-RE-##]. Do not close a risk line without V&V citations per RMP.

### 8. Design changes, residual risk, and RMF

- When a design or process change affects safety, update the RMF, FMEA, and RMP as required; re-run residual risk and risk management review per [SOP-RM-##].
- Document overall residual risk, benefit–risk if required, and risk management report per RMP.

---

## Related Documents

| Document / template | Number | Use |
|---------------------|--------|-----|
| Medical device risk management | [SOP-RM-##] | RMP, RMR, review, PMS |
| Risk evaluation | [SOP-RE-##] | Acceptability, residual after controls |
| Risk analysis (FMEA) | [SOP-RA-##] | Control type, trace IDs |
| Design and development; design change | [SOP-###, SOP-###] | DHF, DCR, release |
| Verification; validation | [SOP-###, SOP-###] | V&V of controls |
| Labeling; usability | [SOP-###, SOP-###] | (3) information for safety |
| Control of quality records; document control | [SOP-RC-##, SOP-DC-##] | RMF records |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| RMP (control priority, V&V expectations) | Risk lead | [Per RMP] | RMF |
| FMEA / control log with (1)-(3) tags and V&V refs | Eng. / Risk | [same] | RMF, eQMS |
| DCRs implementing controls | D&D | [same] | DHF |
| V&V protocols and results for risk controls | QA / Eng. | [same] | RMF / DHF ref. |
| Residual risk, risk management report | Risk lead | [same] | RMF |

---

## Revision History

| Version | Date | Author | Description of change |
|---------|------|--------|------------------------|
| [0.1] | [YYYY-MM-DD] | [##] | Initial issue for review |
| | | | |
| | | | |

---

## Approval Signatures

*Obtain before **Effective Date**. E-signatures allowed if per **[SOP-### Electronic records / 21 CFR Part 11 policy]**.*

| Role | Name | Signature | Date |
|------|------|------------|------|
| Prepared by | | | |
| Reviewed by (Quality) | | | |
| Reviewed by (R&D / Risk) | | | |
| Approved by (Management) | | | |

---

## Appendix A (informative) — ISO 14971:2019 Clause 7 (illustrative)

| Topic | ISO 14971:2019 (illustrative) | This SOP (illustrative) |
|-------|--------------------------------|-------------------------|
| 7, 7.1 | Risk control; priority | Sections 1, 2-4 |
| 7, verification | V&V of control effectiveness | Sections 6-7; V&V SOPs |
| 8, 8.2 | Residual risk, benefit–risk | Section 8; SOP-RM-##, SOP-RE-## |
| D&D, change | 13485 7.3, changes | DCR, DHF; design change SOP |

*Not a substitute for the RMP, DHF, or regulatory submission requirements.*

---

## Appendix B (optional) — Checklist

- [ ] (1)-before-(2)-before-(3) applied; (3) justified when used.
- [ ] Each control has RMP-acceptable trace ID, owner, and status.
- [ ] V&V evidence cited before residual risk is accepted.
- [ ] Design or process change updates RMF and re-estimates residual risk.
- [ ] SOP-R7-## and RMP reviewed on schedule or when controls or use profile change.

---

*End of document*
