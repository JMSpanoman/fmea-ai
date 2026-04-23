<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 14971:2019 — risk analysis (FMEA, FMECA) as structured methods supporting the RMP/RMF.
  SmartRisk: project-based FMEA tables, row-level S/O/D and RPN, components, version history, rule engine, export.
-->

# Risk Analysis (FMEA / FMECA)

---

## Title

**Risk Analysis — Structured FMEA and FMECA (ISO 14971)**

*Shorter public title (optional):* [FMEA / risk analysis]

---

## SOP Number

**[SOP-RA-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Document Owner** | [e.g., Director, Regulatory and Quality / Risk or design assurance lead] |
| **Planned review** | [Annual / when RMP, analysis method, or state of the art practice changes] |
| **Applicable standards** | **ISO 14971:2019;** [ISO 13485:2016; IEC 60601-1, IEC 62304, ISO 10993, IEC 62366-1; ICH Q9 as applicable; MDR, IVDR, 21 CFR 820 as applicable] |
| **Related SOPs** | [SOP-RM-## Risk management; SOP-HI-## or equivalent hazard identification; SOP-### Design and development; SOP-### Software; SOP-### Usability; SOP-### Design change; SOP-RC-##; SOP-DC-##] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **structured risk analysis** using **Failure Mode and Effects Analysis (FMEA)** and, when the **risk management plan (RMP)** requires, **Failure Mode, Effects, and Criticality Analysis (FMECA)** and related methods, in support of **ISO 14971:2019** Clause 5 (risk analysis) and the **risk management file (RMF)** per **[SOP-RM-##].**

This SOP does not replace the RMP, **hazard identification**, or **overall risk acceptability** decisions. It standardizes how the Organization **prepares, performs, scores, records, and approves** FMEA-style analyses so that **failure modes**, **effects**, **causes**, and (when used) **detection** and **RPN** or **criticality** rankings are **traceable**, **reviewed**, and suitable for regulatory and notified body review, including when **SmartRisk** is used as the electronic FMEA **workspace** and **record** source.

---

## Scope

### In scope

- **Design** or **process** (e.g. manufacturing) FMEA as defined in the **RMP** for **[device / IVD / SaMD / product family / process line — as applicable]**, at the **level of analysis** (system, subsystem, **component,** function) specified in the RMP or D&D plan.
- **Preparation,** **team composition,** **scoring,** **documentation,** and **review/approval** for FMEA/FMECA used to support **estimation and evaluation of risk** per **ISO 14971:2019** and the RMP.
- **Electronic** FMEA records in **SmartRisk** (or equivalent) when the RMP and **[SOP-DC-##] / [SOP-RC-##]** allow, including **project**-scoped FMEA **tables,** **rows,** **components,** and **version** or **export** for the RMF.

### Out of scope

- **Enterprise** or **business** risk registers not tied to **device** **safety** and the RMP (unless the RMP explicitly extends scope; if **none,** state **none**).
- Substituting a **numeric** RPN or **internal** detection score for regulatory **benefit–risk** or clinical evidence when those are **required** by applicable jurisdictions; see *Procedure* above and **[SOP-RM-##]** (risk **evaluation** and RMP criteria).

**Justification** for exclusions: **[RMP, quality plan, or RMF index].**

---

## Responsibilities

| Role | Responsibility |
|------|------------------|
| **Risk management lead** (or program manager) | Approves FMEA **scope,** **milestones,** and **link** to RMP/RMF; ensures **residual** and **acceptability** follow **[SOP-RM-##].** |
| **FMEA facilitator / lead** (may be **systems** or **quality** engineer) | **Runs** sessions, enforces **structure,** **versioning,** and **documented** **scoring** rules; ensures **action** **closure** or **formal** **deferral**. |
| **Subject-matter experts (SMEs)** (design, **SW,** **EE,** **ME,** process, **clinical,** as applicable) | Propose **failure modes,** **effects,** and **causes;** own **control** and **V&V** **content** in the **FMEA** and DHF. |
| **Usability** / **HF** (as applicable) | **Use-** and **use-error**-related **modes** and **scenarios;** align with **IEC 62366-1** and usability files when in scope. |
| **RAQA** | SOP and **RMP** **compliance,** **audit-** **ready** FMEA **records,** and **approval** **governance** for **formal** **review** points. |
| **PMS / complaints** (as applicable) | **Post-** **market** inputs that **trigger** FMEA **updates** per the RMP. |

*Team roles in **SmartRisk** map to the **sponsor** and **row** **owners** / **contributors** per **Project** and **FMEA** **governance** in **[WI-XXX / RMP]**. (Replace with Company convention.)*

---

## Procedure

### 1. Risk analysis preparation (inputs and guardrails)

Before populating the FMEA table, the team shall:

1. **Confirm** the RMP (or an approved FMEA plan excerpt): **intended** use, **user** profile, **interfaces,** and **applicable** **standards** (e.g. **IEC 60601-1,** **IEC 62304,** **IEC 62366-1** as applicable).
2. **Obtain** up-to-date **hazard- and scenario-related** inputs (per **[SOP-RM-##]** / **[SOP-HI-##]** or equivalent) so that FMEA failure **effects** can be **tied** to **foreseeable harm** where the RMP **requires** that **linkage**.
3. **Define** the item (or line or function) under analysis, **system boundaries,** and **assumptions** (e.g. **software** release, **configuration,** **sterile** state).
4. **Set** the FMEA type and **convention** (dFMEA, pFMEA, uFMEA or task-based slice, **software** FMEA) per the RMP; one clear **row** **convention** (e.g. one primary failure **mode** per **defined** **component** or function).
5. **Pre-adopt** **scoring scales** and **definitions** (see Section 3); the Organization shall not redefine **severity** or **occurrence** mid-study without a version bump and recorded **justification**.
6. If **SmartRisk** is used: create or open the **Project**; align **components** and **FMEA** rows to the **architected breakdown**; use FMEA version (or export naming) per RMF indexing.

### 2. FMEA / FMECA team and facilitation

- The FMEA **session** shall **include,** as a **minimum,** the **FMEA** **facilitator** and **SMEs** for all major **technological** **areas** in **scope.**
- **SMEs** are **responsible** for the **accuracy** of **failure** **modes,** **causes,** and **proposed** **controls** in their **domain.**
- Where **practicable,** the **facilitator** is not the **sole** **author** of all **rows,** to improve objectivity; the RMP may set **attendance** **rules** for **gated** **reviews.**
- **SmartRisk** workflows (informative, as implemented: project-level FMEA **editing,** **per-row S/O** and **D,** **RPN,** and the **rule engine** and **acceptability** **indicators** when **enabled** per project **configuration**) do **not** **replace** RMP-defined **sign-off;** they **support** **traceability** and **re-evaluation** in the eQMS **record.**

### 3. Severity, probability (occurrence), and detection (when used)

- **Severity (S):** The RMP (or a **FMEA addendum**) **shall** **define** the scale (e.g. 1–N or 1–10) with **examples** that relate FMEA end **effects** to **harm** in line with the RMP and **ISO 14971:2019**. **dFMEA** and **pFMEA** (and other types in scope) **shall** use the **applicable** table; re-mapping to post-market or complaint **severity** **codes,** if any, is **recorded.**
- **Occurrence (O):** Estimates the **likelihood** (or **frequency** class) of the **failure** **mode** or its **cause,** as **defined** in the RMP, for the **relevant** time and use **exposure.**
- **Detection (D),** if used: The RMP **shall** **state** whether the Organization uses **D** and RPN = S × O × D (or S × O only) for **internal** prioritization or **FMECA-**style **criticality.** **D** is how well existing **controls** (inherent design, in-process, or test) **detect** the **failure** **mode** or **cause** before **harm** (per the RMP definition). It is an **organizational** **index,** not a **substitute** for **P1**/**P2** (probability of **harm** under **ISO 14971:2019**); FMEA **outputs** are **reconciled** to the RMP **acceptability** method and **residual-risk** **outcomes** in **[SOP-RM-##].**
- **RPN and alternatives:** Where the Organization uses **RPN** (or S × O or S × O × D only), the RMP or **SmartRisk** project config (e.g. risk **matrices,** **thresholds**) **shall** **define** how high **RPN** or “unacceptable band” rows are **treated,** including **revised** **controls,** **verification,** and re-scoring.
- **Reproducibility:** The FMEA (and the **SmartRisk** project, if used) **shall** keep enough **context** (e.g. **rationale,** **links** to V&V or **standards** **citations**) so that a **reviewer** can **reconstruct** the **S**/**O** (and **D,** if used) **rationale** from the **record.**

### 4. Failure mode identification

- For each **analyzed** item (component, function, or process step), the team **asks** how it **can fail** in **normal** and **relevant** fault or **abnormal** **conditions,** in line with **hazard** and **hazardous** **situation** **coverage** in the RMP.
- **Failure** **mode** text **shall** be **specific,** **testable,** and **distinguishable** from the **effect** and from the **control**; **one** **primary** **mode** per **row** (or per **RMP-defined** **nesting,** e.g. sub-rows in **exports**).
- In **SmartRisk,** each FMEA **row** is a **managed** **record;** **bulk** or **assisted** **row** **creation** (e.g. **AI-suggested** text) **shall** be **reviewed** and **owned** by **SMEs** per the **D&D** plan and **[WI-###].**

### 5. Effects, causes, and (where applicable) linkage to harm

- **Effect(s):** **Local,** then **higher-level,** and if in scope, **patient** or **user**-related **safety** end **effect;** align **terminology** with the RMP or **hazard** **log** where the FMEA **supports** **ISO 14971** **risk** **estimation.**
- **Cause(s):** **Mechanism** of **failure** (design, **material,** **tolerance,** **software** **defect,** process **variability**); **distinguish** the **cause** from the **mode.**
- **Link** to **hazardous** **situation** and **control** **IDs** in the RMF or D&D **artifacts** (e.g. **REQ-###,** **DCR-###** as applicable) as the RMP **requires,** so that **traceability** to V&V and **residual** **risk** is **auditable.**
- **User-related** **modes** and **use** **errors** **shall** follow the RMP and **usability** **plan,** and **shall** **not** **conflate** **O** of a **software** **defect** with **O** of a **user** error **without** an **RMP-stated** **convention.**

### 6. Documentation and records (e.g. eQMS / SmartRisk FMEA)

1. The FMEA (or pFMEA) is an RMF-referenced **record**; **include** or **index** the **version** **identifier,** **date,** and **location** in the RMF.
2. **Version** **control** for FMEA **revisions** (SmartRisk FMEA **version** or **export,** or DMS **pointers)** per **[SOP-DC-##].** Re-analyses after design or process **change** **shall** be **captured** per the **design** **change** SOP **([SOP-###]).**
3. **Row-level** **data** (component, function, **mode,** **causes,** **effects,** S/O, D, **controls,** **actions,** V&V **refs,** **status)** **shall** **remain** **reconstructable;** if RPN is **recomputed,** the S/O (and D) **values** in the **source** **record** are **controlling.**
4. **Exports** (e.g. **CSV,** print-to-PDF) used as the **formal** FMEA “release” **snapshot** to the RMF **shall** **name** the **version** and **include** the **date** and **author** or **approver** as the RMP **requires.**
5. If **SmartRisk** **rule**-**engine** or **acceptability** **badges** are used, **treat** them as **decision** support; the **RMP-defined** **process** in **[SOP-RM-##]** **governs** **release,** **benefit–risk,** and **unacceptable** **risk** **handling.**

### 7. Review and approval

- **FMEA** **readiness** (inputs **complete,** **scoring** **stable,** **major** **open** **items** **closed** or **risk-** **accepted** per the RMP) at **RMP-** and **D&D-defined** **gates,** e.g. design-**output** **lock,** **manufacturing** **qualification,** or **regulatory** **filing.**
- **Approvable** **record** of a **FMEA** **session** or **milestone** (e.g. **minutes,** **e-signature** in the **DMS,** or **formal** **“approved”** **state** in the RMP-**approved** eQMS) with **(a)** **concluded** **scope,** **(b)** **participants,** **(c)** **date,** and **(d)** **unresolved** **hazards** or **RPN** **actions,** if any.
- **RAQA** and the **Risk** **management** **lead** (or RMP-**named** **role)** **verify** GMP- / QMS-**appropriate** **governance,** not **re-inventing** **SME** **technical** **conclusions,** but **verifying** **RMP/RMF** **trace** and **sign-off** **completeness.**
- **Re-open** the FMEA (new **version** or **row** **updates)** on RMP-**defined** **triggers,** e.g. **DCR,** **PMS** **trend,** or **FSCA.**

### 8. Alignment with ISO 14971:2019 (illustrative)

- **Clause 5 (risk** **estimation** **/ analysis):** FMEA is a **structured** way to **support** **risk** **estimation;** the RMP and **Clauses 5,** **6,** and **7** **govern** how **FMEA** **outcomes** **relate** to **residual** **risk,** **risk** **control,** and **control** **effectiveness.**
- **RMP and definitions (Clauses 3, 4):** FMEA **shall** **not** **contradict** the RMP-**stated** **control** **priority: (1)** **inherent** **safety, (2)** **protective** **measures, (3)** **information** for **safety** (see **ISO 14971:2019,** **Clause 7).**

---

## Related Documents

| Document / template | Number | Use |
|---------------------|--------|-----|
| Medical device risk management | [SOP-RM-##] | RMP, RMF, acceptability, residual risk, review |
| Hazard identification (if used) | [SOP-HI-##] | Upstream **hazards/ scenarios** into FMEA effects |
| Design and development; design change | [SOP-###, SOP-###] | DHF, **change** **triggers** for FMEA re-run |
| Document / record control | [SOP-DC-##, SOP-RC-##] | FMEA as controlled RMF **record** |
| Usability / software | [SOP-###] | Use-related and software FMEA **conventions** |
| FMEA / risk matrix / SmartRisk SOPs or WIs | [WI-###] | Scales, RPN policy, eQMS use |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| FMEA (d/p/u/software) and FMECA outputs, versioned | FMEA lead / Eng. | [Life of device + n years, per RMP/retention] | RMF, SmartRisk, or DMS |
| FMEA **review** and **milestone** **sign-** **off** | RAQA / Risk lead | [same] | RMF / eQMS |
| Scoring scale definitions in RMP or annex | Risk lead | [same] | RMP / RMF |
| Change and re-analysis records when FMEA is updated | D&D / [owner] | [same] | DHF / eQMS |

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
| Reviewed by (R&D / FMEA lead) | | | |
| Approved by (Management) | | | |

---

## Appendix A (informative) — ISO 14971:2019 and FMEA (illustrative mapping)

| ISO 14971:2019 (illustrative) | This SOP / FMEA practice (illustrative) |
|--------------------------------|----------------------------------------|
| 3 (definitions), 5.3, 5.4 | FMEA **rows** **support** **hazardous** **situation** and **event** **consideration;** RMP **defines** **formal** **hazard** **log** **link** |
| 5 (estimation) | S/O/ D **per** RMP, **RPN** or **matrix** as **RMP-** **allowed** |
| 6, 7 | FMEA **does** **not** **bypass** **control** **priority;** **controls** **V&V** in **D&D** and RMF |
| 8, 9, 10 | RMR, **review,** and **PMS** **re-** **analysis** **in** **[SOP-RM-##]** |

*Not exhaustive; the **notified** body and the **RMP** govern the detailed mapping (see **[SOP-RM-##]** for full process).*

---

## Appendix B (optional) — FMEA / SmartRisk quality checks

- [ ] RMP **and** FMEA **scope,** **type,** and **assumptions** are **stated.**
- [ ] **Scoring** **definitions** **(S/O/** **D)** are **version-** **controlled** and **not** **changed** **arbitrarily** during the **active** **review** **window.**
- [ ] **Each** **row** has a **mode,** effect(s), and cause(s) **distinguishable** and **SME-** **owned.**
- [ ] **High-** **risk** **(or** **RPN)** **rows** have **timely** **actions,** **controls,** and **V&V** **pointers.**
- [ ] **FMEA** **version** in **SmartRisk** **/ export** **matches** RMF **index.**
- [ ] **Milestone** **approvals** are **in** the RMF.

---

*End of document*
