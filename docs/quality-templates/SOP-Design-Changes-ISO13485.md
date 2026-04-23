<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Clause 7.3.9 (Design and development changes).
-->

# Design and Development Changes

---

## Title

**Design and Development Changes**

*Shorter public title (optional):* [Design Change / DCR]

---

## SOP Number

**[SOP-DCh-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Planned review** | [Annual / when design change regulations or MDR/IVDR practice changes] |
| **Applicable standards** | ISO 13485:2016 (7.3.9); [ISO 14971:2019; IEC 62304; MDR/IVDR; 21 CFR 820.30(i) as applicable] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for how **design and development changes** are **proposed, evaluated, reviewed, approved, implemented, and documented,** so changes are **controlled,** **risk- and regulatory-aware,** and **traceable** in the **DHF** and related **records,** in accordance with **ISO 13485:2016, clause 7.3.9**.

---

## Scope

### In scope

- **Design** and **development** **changes** to **[medical devices, accessories, device software, SaMD — define]** during or after D&D, captured in a **design change request (DCR)** or **eQMS** **equivalent.**
- **Impact** **assessment;** **risk** **assessment;** **re-verification** and **re-validation** **planning;** **approvals;** **documentation** **updates;** and **traceability** **(matrix** / **DHF)** per this SOP and **[SOP-RC-##]**.

### Out of scope

- **Enterprise** QMS or **IT** **changes** with **no** **device** **design** **effect** — **[SOP-###]**.
- **Document** **control** **(format** / **template** **only)** — **[SOP-DC-##]**, unless the change alters **DMR** or **design** **content** **(in** **scope)**.
- **Postmarket** **surveillance** **triage** **only** — **[SOP-###]**, except where a **PMS/PSUR** **outcome** **drives** a **DCR** **(in** **scope)**.
- **Process** or **supplier** **changes** with **no** **design** **output** **effect** — **[SOP-###]**, unless **tied** to a **DCR** **(in** **scope)**.

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **D&D / engineering** | **Initiate** or **lead** the **DCR;** **technical** **impact** **and** **implementation;** **DHF** **updates**. |
| **Design Assurance / QA** | **Process** **conformance;** **DCR** / **eQMS** **workflow;** **approval** **as** **defined;** **independent** **read** where **required**. |
| **Risk management** | **RMF** and **risk** **updates** per **[SOP-Risk-###]**, **linked** **to** the **DCR**. |
| **Regulatory** | **Submission,** **labeling,** **UDI,** **GSPR** **impact;** **reg** **filings** / **notifications** **as** **defined**. |
| **Operations / manufacturing** | **DHR,** **process,** **supplier,** **inventory,** and **changeover** **impact;** **implementation** **readiness**. |
| **Clinical / medical affairs** (if applicable) | **Clinical,** **CER,** **PMCF** **implications**. |
| **Document control** | **Supersession,** **revisions,** **released** **revs** per **[SOP-DC-##]**. |

---

## Procedure

### 1. General (7.3.9)

1.1 The organization **shall** **determine** the **significance** of the **change** to **safety,** **performance,** and **applicable** **regulatory** **requirements,** and **shall** **identify,** **record,** and **control** the **change** in the **DHF** (ISO 13485:2016, **7.3.9**).

1.2 A **design** or **D&D** **change** (except **trivial,** **pre-** **release** **edits** **covered** **in** **[SOP-DDP-###]**) is **managed** as a **DCR** (Section 2) through **implementation** (Sections 3–8).

1.3 **DCRs** **align** **with** **[SOP-DDP-###]** **(phase)**, **[SOP-DR-##]** **(review** when **required)**, and **shall** **not** **bypass** **re-** **V&V** **(Section** **5)** when **warranted**.

### 2. Change requests (CR / DCR)

2.1 **Log** a **DCR** **(or** **ECR** **naming** a **D&D** **change)** using **[form** **DCR-###]** or **eQMS,** with **at** **minimum:**** **originator,** **date,** **affected** **device** **(s)** and **project,** **title,** **proposed** **change,** **reason,** and **(where** **known)** **affected** **documents,** **parts,** or **software** **IDs**.

2.2 **Assign** a **unique** **DCR** **ID,** **status** (e.g. **draft,** **under** **assessment,** **approvals,** **implemented,** **closed)**, and **a** **single** **D&D** **owner** for **assessment**.

2.3 **Urgent** **/**** **field-** **action-** **linked** **changes** may **use** an **expedited** **path** **(parallel** **reviews,** **time** **boxes)** per **[SOP-###]**, but **shall** **not** **omit** **documented** **safety,** **risk,** and **regulatory** **touches;** **record** the **expedited** **plan** in the **DCR**.

### 3. Impact assessment

3.1 For **each** **DCR,** **complete** an **impact** **assessment (IA)** covering, **as** **applicable:**** **(a)**** **design** **inputs** and **outputs;** **(b)**** **BOM,** **drawings,** **software** **(build,** **SII,** **SOUP)****;** **(c)**** **labeling,** **IFU,** **languages;** **(d)**** **manufacturing** and **inspection;** **(e)**** **DHR,** **materials,** **inventory;** **(f)**** **suppliers** and **subassemblies;** **(g)**** **regulatory** **(submission,** **GSPR,** **class,** **UDI)****;** **(h)**** **PMS,** **complaints,** **trends;** **(i)**** **usability,** **cyber,** **clinical,** **CER;** **(j)**** **schedule** and **resource.**

3.2 **Categorize** the **change** (e.g. **minor,** **major)**** **per** **company** **criteria** **[DOC-###]**, **linked** to **7.3.9** **“significance”** and **RDC** / **regulatory** **policy**.

3.3 **Record** the **IA** **conclusion** in the **DCR**; **reference** **affected** **documents,** **parts,** and **matrices** **as** **needed**.

### 4. Risk assessment (ISO 14971)

4.1 **Assess** or **update** **hazards,** **harms,** and **control** **effectiveness** **affected** by the **DCR**; **link** to **HARA,** **hazard,** or **RMF** **IDs** per **[SOP-Risk-###]**.

4.2 **Record** **residual** **risk,** **benefit–risk,** and **(where** **required)** **RMF** **/**** **RMS** **evidence** in the **DCR** and **RMF** **before** full **implementation**, **unless** a **formally** **approved** **interim** **release** **with** **controls** is **in** **place**.

4.3 **Do** **not** **close** the **DCR (Section** **8)** with **unmitigated** **safety-** **critical** **gaps**; **use** **CAPA** if **a** **broader** **containment** is **required** per **[SOP-###]**.

### 5. Re-verification and re-validation

5.1 **Identify** **affected** **design** **inputs,** **outputs,** and **/****or** **user** **needs** in the **trace** **matrix**; **define** **re-** **verification (DVer)** and **/****or** **re-** **validation (DVal),** and **software** **V&V,** per **[SOP-DV-##]**, **[SOP-DVal-##]**, and **[SOP-###] / IEC 62304**.

5.2 **Update** the **V&V** **plan** **[VVP-###]**, **D&D** **plan** **section,** or **a** **DCR** **V&V** **addendum** with **activity** **IDs,** **acceptance** **criteria,** and **rationale** if **V&V** is **not** **repeated** **(with** **D&A** **/**** **risk** **concurrence)****.

5.3 **Capture** **DVer,** **DVal,** **(or** **HFE)**** **protocol** and **report** **references** in the **DCR** **/**** **DHF** **before** or **in** **step** **with** **implementation,** per **DCR** **priority**.

5.4 If the **change** **affects** **design** **transfer** **/**** **first** **production,** or **process** **validation,** follow **[SOP-DT-##]** and **[SOP-###] (process** **validation)** and the **IA**.

### 6. Approvals

6.1 **Approvers** **by** **change** **category** are **in** **[DOC-###]****;** at **minimum** **include:**** **(a)**** **D&D** / **engineering;** **(b)**** **Design** **Assurance** / **QA;** **(c)**** **regulatory,** when **IA** **/**** **risk** **/**** **labeling** **requires;** **(d)**** **manufacturing** / **operations** when **BOM** or **DHR** **affected;** **(e)**** **other** **roles** **(clinical,** **HFE)**** as** **listed** **in** the **DCR**.

6.2 **Invoke** a **design** **review** per **[SOP-DR-##]** for **significant** **/**** **major** **changes** (define in **[DOC-###]****),** or a **dedicated** **“change** **review”** **if** not a **full** **DR** **milestone**.

6.3 If **e-signatures** **are** **used,** **comply** **with** **internal** **policy** **/**** **21** **CFR** **Part** **11** **[SOP-###]****.**

6.4 **Do** **not** **release** **updated** **DMR** / **affected** **manufacturing** **documents** to **routine** use **until** **approved,** **except** **(if** **defined)** **R&D** **/**** **pilot** **builds** with **DHR** **/**** **QC** **conventions** per **[SOP-###]**.

### 7. Documentation updates

7.1 **After** **approval,** **revise** or **supersede** **affected** **DHF,** **DMR,** **BOM,** **drawings,** **WIs,** **travellers,** **labeling,** **IFU,** **RMP,** **RMF,** **trace** **matrix,** **CER,** and **/****or** **software** **/**** build** **records,** per **[SOP-DC-##]**, **PLM,** and **eDMS** **rules**.

7.2 **Record** **effective** **dates,** **revision** **history,** **and** **cut-** **in** **(as** **used** **on)** or **field** **transition** **rules** in the **DCR** as **applicable**.

7.3 For **device** **software** **/**** **SaMD,** **update** **SII,** **SVD,** and **release** **records** per **IEC** **62304** **[SOP-###]**.

7.4 **Execute** **UDI,** **EUDAMED,** **/**** **FDA,** and **/****or** **regulatory** **notifications** per **[SOP-###]****.**

### 8. Traceability and closure

8.1 **Update** the **trace** **matrix** **[SOP-DI-###, DOC-###]** so **each** **affected** **row** **references** the **DCR** **ID,** **new** or **updated** **V&V,** and **(where** **applicable)**** **risk** **control** **IDs**.

8.2 The **closed** **DCR** **shall** **link** the **change** **request,** **IA,** **risk,** **approvals,** **V&V,** **regulatory** **actions,** and **DHR** / **implementation** **evidence,** and **reside** in the **DHF** / **device** **file**.

8.3 **Set** the **DCR** **to** **closed** **only** when **(a)**** **required** **V&V** **is** **complete** **(or** **N/A** **is** **approved)****,** **(b)**** **docs** / **DMR** **/**** **labeling** **/**** **SW** **rev**s **are** **released,** **(c)**** **RMF** **is** **consistent,** and **(d)**** **production** **/**** **inventory** **transition** is **as** **planned** **(unless** **QA-** **approved** **waiver)****.

---

## Related Documents

| Document | Number |
|----------|--------|
| Design and development plan | [SOP-DDP-###] |
| Design inputs; trace matrix | [SOP-DI-##], [DOC-###] |
| Design review | [SOP-DR-##] |
| Design verification | [SOP-DV-##] |
| Design validation | [SOP-DVal-##] |
| Design transfer | [SOP-DT-##] |
| Risk management | [SOP-Risk-###] |
| Software lifecycle (IEC 62304) | [SOP-###] |
| Change control (general) | [SOP-###] |
| Control of documents | [SOP-DC-##] |
| Control of quality records; DHF | [SOP-RC-##] |
| Postmarket; vigilance | [SOP-###] |
| Usability (IEC 62366-1) | [SOP-###] |
| Process validation | [SOP-###] |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| DCR / eQMS | D&D / QA | [Per DHF] | [eQMS] |
| Impact assessment, risk links | D&D / Risk | [Per DHF] | [eDHF] |
| DVer / DVal (as triggered) | R&D / QA | [Per DHF] | [eDHF] |
| Updated DMR, labeling, RMF, trace matrix | DCC / D&D / RA | [Per device file] | [eDMS / eQMS] |
| Regulatory filing / UDI notification (as applicable) | Regulatory | [Per reg policy] | [UMS] |

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
| Reviewed by (R&D) | | | |
| Reviewed by (Regulatory, as applicable) | | | |
| Approved by (Management or D&D Director — define) | | | |

---

## Appendix A — ISO 13485:2016 mapping (informative)

| Clause | Expectation | This SOP |
|--------|-------------|----------|
| 7.3.9 | Changes: **significance,** **safety,** **performance,** **reg,** **identify,** **record,** **control** in **DHF** | §1–8 |
| 7.1 | **Planning** of **product** **changes** (context) | [SOP-###] |
| 4.2.4 | **DHF** (includes design change) | [SOP-RC-##] |
| 7.3.2 | **D&D** plan **(updates)** | [SOP-DDP-###] |
| 7.3.4 to 7.3.8 | **Outputs,** **review,** **V&V,** **transfer** **(may** **re-run)** | Cross-referenced SOPs |

---

## Appendix B (optional) — Audit checklist

- [ ] DCR/IA and significance to safety/performance/reg is on file; RMF link where design affects risk.
- [ ] V&V plan (or N/A with concurrence) matches affected requirements; re-DVer / re-DVal as justified.
- [ ] Approvals match company matrix for change category; DR invoked when required.
- [ ] DMR, labeling, IFU, software revs, and trace matrix updated; DHF is coherent.
- [ ] DCR not closed with open safety or regulatory gaps without approved waiver; CAPA if required.

---

*End of document*
