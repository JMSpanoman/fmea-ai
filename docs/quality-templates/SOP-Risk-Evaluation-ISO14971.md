<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 14971:2019 — risk evaluation (Clause 6): estimated risk vs acceptability criteria.
  Cross-references: RMP, RMF, risk analysis, risk control, benefit–risk, record control.
-->

# Risk Evaluation

---

## Title

**Risk Evaluation (ISO 14971 — Clause 6)**

*Shorter public title (optional):* [Risk acceptability / evaluation]

---

## SOP Number

**[SOP-RE-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Document Owner** | [e.g., Director, Regulatory and Quality / Risk management lead] |
| **Planned review** | [Annual / when RMP, acceptability policy, or state of the art changes] |
| **Applicable standards** | **ISO 14971:2019;** [ISO 13485:2016; MDR, IVDR, 21 CFR 820; IEC 60601, IEC 62304, IEC 62366-1, ISO 10993 as applicable] |
| **Related SOPs** | [SOP-RM-## Risk management; SOP-RA-## Risk analysis / FMEA; SOP-### Design and development; SOP-### Design change; SOP-### CAPA; SOP-RC-##; SOP-DC-##] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **risk evaluation** per **ISO 14971:2019, Clause 6** — comparing **estimated risk** (from **Clause 5** and the **risk management plan (RMP)**) to **risk acceptability criteria** — and for **documenting** **acceptable,** **unacceptable,** and (if used) **ALARP** or other RMP-defined outcomes in the **risk management file (RMF)** per **[SOP-RM-##].**

The **RMP** is the **authoritative** source of **acceptability** policy for each device and **jurisdiction**; this SOP defines **how** the Organization **applies** that policy, **records** **accept/reject** decisions, and **escalates** **unacceptable** **risks** to **risk control,** **review,** and **benefit–risk** when the RMP or applicable regulation requires.

---

## Scope

### In scope

- **Evaluation** of **estimated** risk (after **risk** **estimation** per the RMP — e.g. FMEA, qualitative scoring, or **P1** / **P2** as the RMP defines) **against** **RMP-approved** **acceptability** **criteria** for **[device / IVD / SaMD / product family — as applicable]**
- **Use** of **matrices,** **policy** rules, **numeric** **thresholds** (e.g. FMEA RPN or eQMS rule output when the RMP allows), and **narrative** **rationale,** as stated in the RMP
- **Records** of **decisions,** **escalation,** and **required** **reviews** for **regulatory** and **notified** **body** review

### Out of scope

- **Regulatory** or **strategic** decisions about **jurisdictions** and **submissions** alone (handled in the **RMP** and **regulatory** process)
- **Enterprise** or **non–device-**safety **risk** registers, unless the RMP **explicitly** extends scope (if **none,** state **none**)

**Justification** for out-of-scope items: **[RMP, quality plan, or RMF index]**

---

## Responsibilities

| Role | Responsibility |
|------|------------------|
| **Risk** **management** **lead** | Maintains or governs the **RMP;** **acceptability** **criteria,** **review** **gates,** and **escalation;** **RMF** **completeness** for **Clause 6** |
| **RAQA** | **Auditable** **records,** **SOP** **adherence,** and linkage to **QMS** (e.g. **CAPA,** **change** **control**) |
| **Design** **&** **development** / **SMEs** | **Perform** **evaluation;** **propose** **controls** for **unacceptable** or **ALARP-bounded** items per the RMP |
| **Clinical** / **regulatory** (as **applicable)** | **Benefit–** **risk** and **state** of **art** per the RMP |
| **Top** **management** | As **RMP-** **defined** for **significant** **residual** or **benefit–** **risk** **decisions** |
| **PMS** / **complaints** | **Re-evaluation** **triggers** per the **RMP** / **[SOP-RM-##]** |

---

## Procedure

### 1. Risk acceptability criteria (RMP and RMF)

- The RMP (per **ISO 14971:2019** 4.4) shall define **risk acceptability** **criteria** before the first **formal** **evaluation** at a **milestone,** or **concurrently** with **justification;** **criteria** are **recorded** in the **RMF** or RMP **annex,** not ad hoc
- **Criteria** may use **qualitative** **bands** (e.g. **acceptable,** **ALARP,** **unacceptable**), **matrix** **cells,** **cut-offs,** or **P1**/**P2** **comparisons;** the RMP **names** the **default** **method** (e.g. **S**×**O** **vs** FMEA-to-**criterion** **mapping)**
- When **criteria** **change,** **version** the RMP (or addendum) and **re-evaluate** **affected** **open** **risks** per **design** **change** and RMP **rules** **[SOP-###]**

### 2. “Estimated risk” in this SOP

- **Estimated** **risk** is the **output** of **risk** **estimation** (**Clause** **5**) in the form the RMP **prescribes** (e.g. **S**+**O,** **P1** and **P2,** or **FMEA-** **derived** **values** for **triage** only where the RMP **permits)**
- The team **shall** **not** use **raw** FMEA RPN (or S/O) as **P1**/**P2** **acceptability** **without** a **documented** **translation** in the **RMP/RMF** where **regulators** expect **harms-** **based** **estimates**

### 3. Severity, probability, matrices, and eQMS

- **Severity (S),** or RMP equivalent for harm seriousness: use the RMP-defined scale and example anchors, aligned with hazard and analysis terms.
- **Occurrence (O)** and **P1** / **P2** (probability of harm) where used: follow RMP definitions and stated exposure (e.g. per use, per device-year).
- **Matrix:** If the RMP uses an S×O (or P1 and P2) matrix, each cell maps to one stated outcome (acceptable, unacceptable, or ALARP with next action); version the matrix in the RMF.
- **FMEA** RPN and eQMS support (e.g. **SmartRisk**): the RMP-aligned outcome after required review is the recorded accept/reject decision; automation or badges alone are insufficient unless the RMP allows it.

### 4. Matrix, policy, and accept or reject documentation

- For each evaluated risk (or FMEA row, as RMP-structured), the RMF (or eQMS export) shall include: (a) identifier, (b) inputs to estimated risk, (c) criterion or cell, (d) decision (acceptable, unacceptable, ALARP, or other RMP label), (e) date, role, or link to review minutes.
- Unacceptable decisions shall not close without a path to risk control (Clause 7) per **[SOP-RM-##]** or RMP-permitted exception (e.g. halt, scope reduction) documented in the RMF or DCR.
- If **ALARP** (or **ALARA** per RMP) is used, the RMP shall define what further reduction or documentation is required for risks in that band.

### 5. Escalation of unacceptable risks

- Unacceptable estimated risks (per the RMP) shall be escalated (timings in RMP):
  1. Start or accelerate risk control and change per **[SOP-RM-##]**; do not release on accept by default.
  2. If residual risk stays unacceptable, escalate to benefit–risk and RMP- or jurisdiction-defined approvers (e.g. top management) per **[SOP-RM-##]**.
  3. If post-market data warrant, use PMS, CAPA, FSCA SOPs and RMP re-evaluation.
- Log escalations (e.g. change order, RMF entry) so RAQA and management see open actions.

### 6. Review requirements

- RMP-planned reviews shall cover: (a) evaluations vs current criteria, (b) open unacceptable or ALARP actions, (c) re-evaluation after change or PMS triggers.
- Before RMP-defined gates (e.g. design output lock, CE or first marketing), the Risk management lead (or delegate) shall confirm that no unaddressed unacceptable risks block the gate unless an RMP-documented waiver (rare) or approved benefit–risk is in the RMF.
- Post-market re-evaluation per **ISO 14971:2019** Clauses 9 and 10 and **[SOP-RM-##]**.

---

## Related Documents

| Document / template | Number | Use |
|---------------------|--------|-----|
| Medical device risk management | [SOP-RM-##] | RMP, RMF, benefit–risk, risk control |
| Risk analysis (FMEA) | [SOP-RA-##] | Estimation inputs, matrix / RPN |
| Design and development; design change | [SOP-###, SOP-###] | Gates, re-evaluation triggers |
| Document / record control | [SOP-DC-##, SOP-RC-##] | RMF and evaluation records |
| CAPA, PMS, complaints | [SOP-###, …] | Post-market escalation |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| RMP and acceptability criteria (versioned) | Risk lead | [Per RMP / retention policy] | RMF |
| Risk evaluation log / FMEA with outcome | Eng. / Risk | [same] | RMF, eQMS |
| Review minutes for evaluation gates | Risk / RAQA | [same] | RMF |
| Escalation and benefit–risk records | As RMP | [same] | RMF |

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

## Appendix A (informative) — ISO 14971:2019 Clause 6 (illustrative)

| Topic | ISO 14971:2019 (illustrative) | This SOP (illustrative) |
|-------|-------------------------------|-------------------------|
| RMP, acceptability | 4, 4.4 | Sections 1–2; RMP is authority |
| Estimation to evaluation | 5 to 6 | Sections 2–4 |
| Risk control | 7 | Section 5; [SOP-RM-##] |
| Residual, benefit–risk | 8, 8.2 | Section 5; [SOP-RM-##] |
| Management review, PMS | 9, 10 | Section 6; [SOP-RM-##] |

*Not a substitute for the RMP, regulatory submission, or notified body expectations.*

---

## Appendix B (optional) — Checklist

- [ ] RMP has versioned acceptability criteria for the device and intended use.
- [ ] Severity and probability (or P1/P2) scales are clear; FMEA mapping is documented if FMEA is used.
- [ ] Matrix or policy in use is RMP-approved and RMF-referenced.
- [ ] Unacceptable or ALARP items have owners and dates or approved benefit–risk.
- [ ] Gate reviews and PMS triggers are current in the RMF.
- [ ] SOP-RE-## and RMP criteria revisited on schedule or when regulation or use changes.

---

*End of document*
