<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Clause 7.3.6 (Design and development validation).
-->

# Design Validation

---

## Title

**Design Validation**

*Shorter public title (optional):* [Design Validation / DVal]

---

## SOP Number

**[SOP-DVal-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Planned review** | [Annual / when user population, use environment, clinical, or HFE strategy changes] |
| **Applicable standards** | ISO 13485:2016 (7.3.6); [ISO 14155:2020; ISO 18113; IEC 62304; IEC 62366-1; MDR/IVDR; 21 CFR 820.30(g) as applicable] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **planning, conducting, documenting, and approving** **design validation** so the **medical device** (including labeling and instructions for use when in scope) is **shown to meet** **user needs** and the **stated** **intended use**, in accordance with **ISO 13485:2016, clause 7.3.6**. Design validation answers: **“Did we build the right product for the right users and use?”** It is **complementary** to **design verification** — which confirms design outputs **against design inputs** — in **[SOP-DV-##]**.

---

## Scope

### In scope

- **Validation** for **[medical devices, accessories, device software, SaMD — define]** as scheduled in the **design and development plan** **[SOP-DDP-###]** and the **V&V plan** **[VVP-###]**, with **DHF** records per **[SOP-RC-##]**.
- **Validation planning**; user and use **environment**; **simulated** and/or **actual** use; **clinical** evidence or studies when **applicable**; **pre-defined** **acceptance criteria**; **protocols**, **reports**, and **traceability** to user needs; **re-validation** after **significant** **design** **changes** per **[SOP-###]**.

### Out of scope

- **Design verification** (design input conformance) — **[SOP-DV-##]**.
- **Process validation (IQ/OQ/PQ)**, including manufacturing process, cleaning, and sterilization validation as separate SOPs — **[SOP-###]**.
- **Usability** engineering **recordkeeping** in full — this SOP references **[SOP-###] / IEC 62366-1** and defines how **summative** and/or **DVal-integrated** evidence is **captured and approved** for 7.3.6.
- **Postmarket surveillance and PMCF** **operations** — **[SOP-###]**, **except** where a validation activity **feeds** **DHF** **or** the **CER/PRRC** as **stated in the protocol** (e.g. registry-style follow-up in **protocol**, not PMS in lieu of 7.3.6 when not justified).

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **D&D / validation lead** | Owns validation planning, protocols, and schedule; ensures **user-need and intended-use** trace, **DHF** completeness, and **closure** of open items before the validation gate. |
| **Test / study execution owners** | Execute protocols per training; collect **objective** evidence; record **deviations**; maintain privacy and good clinical / human-subjects practice where **applicable**. |
| **Design Assurance / Quality** | Reviews/approves protocols and reports; **independent** review of conclusions where **Section 3.4** applies; final **readiness** for 7.3.6. |
| **Independent reviewer** (when required) | Confirms that use scenarios, methods, and conclusions are **defensible** and not only authored by the design **owner** (per **Section 3.4**). |
| **Regulatory (as applicable)** | Aligns validation package with **submission** strategy, MDR/IVDR **clinical** and **CER** expectations, and any **GSPR**-linked claims supported by DVal. |
| **Clinical / medical affairs (if applicable)** | Clinical protocol content, **IRB/ethics**, **safety** reporting, **adverse** events, and **ISO 14155**-aligned study conduct per **[SOP-###]**. |
| **Human factors / usability (if applicable)** | **Use** environment, **formative** inputs, **summative** test plan, and **integration** with DVal as defined in the **HFE/IFU** and **[SOP-###]**. |

---

## Procedure

### 1. General requirements (7.3.6)

1.1 **Design validation** shall be **planned** and **documented** before a validation gate is used for design transfer, submission, or other declared milestone, as stated in the **design and development plan** and **V&V** plan **[SOP-DDP-###, VVP-###]**. Validation is performed on **manufacturing-equivalent** product (or a pre-production build with **documented** justification in the plan), the **intended** shipped configuration, and the **in-scope** IFU, labeling, and accessories as listed in the DVal **protocol** — unless a **stated** **exception** (e.g. pilot build with DHR reference) is **approved in the protocol** and does **not** invalidate the intended use claim.

1.2 Where the standard requires validation using **the device** itself, use the device under test. Where that is **impracticable**, use a **representative** and **record** the rationale. Where the standard refers to use of **manufacturing** equipment, align the test setup with the **V&V** / DVal plan and the DHR or equivalent for that build, per project rules.

1.3 **Design validation** is **distinct in intent** from **design verification** **[SOP-DV-##]**: the evidence set shall **link** to **user needs** and **intended use** (or **user-oriented** requirements in the **trace** **matrix**), not only to design inputs. Where a **single** test supports both a design input and a user need, the **trace** **matrix** and **DValR** shall name both links **explicitly**.

1.4 **Software, firmware, and SaMD** also follow the **software** lifecycle **SOP** **[SOP-###] / IEC 62304**. This SOP governs **7.3.6** **protocols**, **report** structure, **approvals**, and **DHF** records for the **user-need and intended-use** conclusion, including links to any **non-clinical** and **clinical** **strategy** **documents** in the **DHF**.

### 2. Validation planning (DValP / V&V)

2.1 The **V&V plan** **[VVP-###]**, or a stand-alone design validation plan **(DValP)** in **[DOC-###]**, shall, before executing relevant validation activities, state at **minimum** for the activity or milestone:

- Product name, project, and design milestone;
- **User** need and **intended use** (or URS) **IDs** in **scope**;
- **User** and **use** **environment** assumptions (see **Section 3**);
- Whether validation uses **simulated** use, **actual** use, or **both** (see **Section 4**) and the **rationale**;
- Whether **clinical-** type evidence or **HCP-** **facilitated** assessment is used (see **Section 5**);
- **Build** / **configuration** level, **prerequisites** (e.g. completed DVer, training, summative as applicable);
- **Pre-defined** **acceptance** **criteria** (see **Section 6**);
- **Risks**, **known** **limitations**, and any **independent** review or **second** signatory (see **Section 3.4**).

2.2 **Revisions** to the DValP follow **change** **control** **[SOP-###]**. A revised plan that changes **scope,** **methods,** or **acceptance** shall trigger a **re-assessment** of **open** or **unexecuted** **protocols**.

2.3 For **pivotal** or **submission-relevant** validation, the plan shall **cross-reference** the **CER,** **CIP,** and **MMA/PMCF** **interfaces** per **regulatory** **templates** **[DOC-###]**, as **applicable** to jurisdiction and **device** **class**.

### 3. User and use environment

3.1 The DVal **protocol** shall state the **intended** user (role, **training** level), the **patient** or **anatomical** model when **relevant,** **exclusions,** and any use of **simulated** or **stand-in** users, with **rationale** for **fidelity** versus **intended** target users.

3.2 The **use** **environment** (e.g. home, acute care, **OR,** **ambulatory,** connectivity and HIT) shall be **described** in enough detail to show **fidelity,** **controls,** and **gaps** versus **foreseeable** use. Summarize the same in the **DValR** so a **conformity** or **regulatory** **assessor** can follow the design **validation** story without hunting through **appendices**.

3.3 If **HFE/62366-1** **summative** **evaluation** is **separate** from a **named** DVal **run,** the DValP and the **HFE** **file** **shall** **cross-** **reference** each other, and a **synchronized** view of user needs (trace **matrix** or **HFE-IF**) **shall** show which needs are met by **summative,** by **DVal,** or by **both,** without **gaps** or a **duplicated** pass **without** **rationale**.

3.4 Where the **DValP** **requires** **independent** **review,** the **reviewer** **shall** be **competent** and **sufficiently** **independent** of the design **(not** the **sole** **author** of the **device** under **test,** per **project** **policy)****,** in **line** with the **independence** **principles** in **[SOP-DR-##]** and **[SOP-DV-##]****,** as **analogous** to **DVer.**

### 4. Simulated and actual use

4.1 **Simulated** use may **include** bench testing, **task-** **based** exercises, HIT or **connectivity** test beds, cadaver or model work, and in-lab procedures, **provided** **fidelity** and **limits** are **stated** in the **protocol**.

4.2 For **actual** use in **intended** or **reasonably** **foreseeable** settings where use is **authorized** and **ethical,** **document** site, duration, and any PMS-**relevant** observations only as **pre-specified** in the **protocol;** do **not** use ad hoc PMS data as a substitute for **7.3.6** **closure** unless the DVal plan and **regulatory** **rationale** **explicitly** support that **link**.

4.3 The DValP and DValR shall **justify** that the **combination** of **simulated** and/or **actual** use is **sufficient** to support the **stated** **intended** **use** and GSPR- or **indication-** **relevant** **claims** in **scope** for the **device,** including MDR **Annex I-** type aspects where the **regulatory** **file** **maps** them to **DVal.**

### 5. Clinical considerations (when applicable)

5.1 When design validation **uses** a **clinical** **investigation,** pre-specified **registry-based** data, or **HCP-** **directed** in-clinic assessment of **safety** and **performance** linked to user needs, the work shall follow **[SOP-###]**, **ISO 14155:2020** where **applicable,** and **applicable** **ethics** (IRB/EC as **required)****.**** A **CER-**independent (RA + clinical) **safety** / **performance** read of **pivotal** or DVal-**gating** **results** shall occur before **DValR** is signed to **pass.**** SUSAR,** **vigilance,** and **reporting** follow **[SOP-###]****.**

5.2 When no interventional or **subject-** **facing** **clinical** data are **required,** the **DValP** **records** a **non-** **clinical** strategy and **(optional)**** **rationale (e.g.**** **well-** **established-** **technology** path)****;** **validation** may then use **e.g.**** **summative,** **cadaver,** or HCP-**unaided** **tasks** as **defined** in the **protocol.**

5.3 A **failed** DVal, a **serious** **adverse** event, or a **new** **safety** **signal** **shall** **not** be **reconciled** to a **passing** DValR without **CAPA,** design **/ change,** and **re-** **execution** or a **formal** **risk-** **based** **waiver** per **[SOP-###]****.**

### 6. Validation acceptance criteria

6.1 **Acceptance** **criteria** **shall** be **in** the **protocol** (or a **pre-approved** **amendment**) before results **affect** **7.3.6** **closure.**** They may be **task-** **based (e.g.** SUS-** **linked)**,** **operational,** or **outcome-** **measured,** and **shall** **map** to **at least** one **in-scope** **user** need or **intended-** use **line.**

6.2 **Subjective** **success (e.g.** user **preference** **only)** is **inadequate** **unless** **paired** with **observable,** **verifiable,** or **analytic** **evidence** in the same **protocol (e.g.** use **errors,** time-**on-** **task)****.**

6.3 **Post-** **hoc** **"pass"** redefinition, **dropping** **unfavourable** **endpoints,** or **excluded** data is **not** **permitted** without a **formal** **amendment** and re-** **approval,** and **independent** **review** where **Section 3.4** of this SOP **applies.**

### 7. Protocols, execution, and deviations

7.1 **Design** **validation** (DVal) **protocols** use **[template DValP-###]** (or the eQMS form) with at **minimum:**** **purpose** and **scope;** user and **use** **environment;** **device** / **software** **config;** **procedures;** data to **collect;** **acceptance** **criteria;** **roles,** **training,** and sign-**off** **blocks.**

7.2 **Execute** only **approved,** **released** **protocols.** Deviations **(same** **discipline** as **[SOP-DV-##]** and **[SOP-###]****)****:**** **assess** **impact** on **7.3.6** **validity;** **escalate** to **Design** **Assurance;** do **not** "pass" a DValR on a run **affected** by a **material** **deviation** without **assessment** and **documented** **disposition.**

### 8. Traceability to user needs and intended use

8.1 The **requirements** / **trace** **matrix** **[SOP-DI-###, DOC-###]**, or a **validation-** only **addendum,** **shall** for **each** **in-scope** **user** need **list:**** **(a)**** DVal **protocol** **ID,** **(b)**** DValR **ID,** and **(c)**** **outcome** (Pass, Fail, or N/A with **rationale)****.**

8.2 Aspects of DVal that **mitigate** use-**error-** **related** **risks** **shall** **link** to **hazard,** **control,** or **inspection/ testing** in the RMF/UE per **[SOP-Risk-###]** and **[SOP-###]****.**

### 9. Design validation report (DValR)

9.1 Each DValR (or **approval** of a **protocol+** **evidence** **package)**** **shall** **include** at **minimum:****

- **Protocol** (and **amendment)**** **IDs** and **version**s**;
- **Device,** **software,** and **label** in **scope;**
- **User,** **patient,** and **use** **environment;**
- **Tabulated** or **structured** **summary** of **results** **vs.**** **acceptance;**
- **Known** **limits** and **residual** **gaps,** and **rationale** for **sufficiency;**
- **Conclusion:**** **stated** **user** **needs and intended** **use** met or **not;**
- Pointers to all **objective** **evidence;**
- **Regulatory** or **study** **references** (CER, **IDE,** **SRN,** as **applicable)****;**
- **Approved** signatories: **D&D** / **validation** lead; **Design** **Assurance** / **QA,** and **other** **roles (Reg,** **Clinical,** **HFE)**** as **in** the **DValP.**

9.2 **Failed,** **partial,** or **inconclusive** **results** **shall** **not** mark **7.3.6** as "complete" in the **matrix** until **re-** **test,** **design** **change,** or a **formal** **risk-** **based** **waiver** with **RA/****QA** and as **per** **[SOP-###]****.**

### 10. Final approval and design review

10.1 **Final** sign-**off** of **DValR** and **7.3.6** **readiness** **shall** follow **[SOP-DR-##]** and/or a **controlled** eQMS **route** for DValR **approval,** with **(a)**** D&D** / **validation** lead, **(b)**** **Design** **Assurance/QA,** and **(c)**** other **stakeholders** (Reg, **Clinical,** **HFE)**** as **defined** in the **DValP.**

10.2 **Do** **not** **declare** a D&D **milestone** "validation** **complete"** (e.g. design **transfer,** **regulatory** **submission)**** without **(a)**** an **approved** DValP **or** VVP and **DValR** (or **package)**** for **in-scope** **user** **needs,** **(b)**** no **unacceptable** **open** **deviations** on **DVal,** and **(c)**** PMS/PMCF** follow-**on** as **captured** in the **CER,** if **jurisdiction** or **SOP-** level **obligations** require **it.**

---

## Related Documents

| Document | Number |
|----------|--------|
| Design and development plan | [SOP-DDP-###] |
| V&V plan; trace matrix (user needs) | [VVP-###], [DOC-###] |
| Design inputs | [SOP-DI-##] |
| Design verification (complementary) | [SOP-DV-##] |
| Design review | [SOP-DR-##] |
| Change control; D&D changes | [SOP-###] |
| Human factors / usability; IEC 62366-1 | [SOP-###] |
| Risk management | [SOP-Risk-###] |
| Software lifecycle; IEC 62304 | [SOP-###] |
| Control of documents | [SOP-DC-##] |
| Control of quality records | [SOP-RC-##] |
| Clinical / ISO 14155; ethics (if used) | [SOP-###] |
| Postmarket surveillance; vigilance (reference) | [SOP-###] |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| V&V plan; DValP | D&D / validation | [Per DHF] | [eDHF] |
| DVal protocols and revisions | R&D / QA | [Per DHF] | [eDHF] |
| **Raw** data, logs, photos, ePRO, study CRFs (if any) | Study team / R&D | [Per DHF / **clinical** policy] | [controlled path] |
| Deviations, amendments | QA / D&D | [Per DHF] | [eDHF] |
| DValR and approvals; updated trace for user needs | D&D / QA | [Per DHF] | [eDHF / eQMS] |

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
| Reviewed by (R&D / Validation) | | | |
| Reviewed by (Regulatory, if applicable) | | | |
| Approved by (Management or D&D Director — define) | | | |

---

## Appendix A — ISO 13485:2016 mapping (informative)

| Clause | Expectation | This SOP |
|--------|-------------|----------|
| 7.3.6 | Validation to ensure the device **meets user needs and intended use**; as appropriate, **test** using **manufacturing** equipment; **where practicable,** validate using **the device itself**; **where impracticable,** validate using **a representative (document why)**; **retain** records. | §1–6, §8–10; **3.4** (independent review) |
| 4.2.4 | Design and development (DHF) | [SOP-### / RC-##] |
| 4.2.5 | Control of quality records (validation records) | [SOP-RC-##] |
| 7.3.2 / 7.3.3 / 7.3.4 | Inputs, outputs, review (context) | [SOP-DI-##], [SOP-###], [SOP-DR-##] |
| 7.3.5 | Verification (complement) | [SOP-DV-##] |

---

## Appendix B (optional) — Audit checklist

- [ ] DValP/VVP shows which **user needs / intended use** are validated, **how**, and **before** execution.
- [ ] DVal used **manufacturing-equivalent** (or **documented** equivalent) and **in-scope** labeling/IFU as applicable.
- [ ] User, patient (if any), and **use** environment are defined; sim vs. actual is justified; clinical follows ethics/SOPs when used.
- [ ] Acceptance criteria are **pre-defined** and **mapped** to user needs; deviations are **assessed**; no silent post-hoc pass.
- [ ] DValR concludes **met / not met**; trace matrix (or equivalent) links **user need** → **protocol** → **report** → **outcome**.
- [ ] Independent or Design Assurance sign-off is present per project rules; 7.3.6 is not "complete" on failed validation without **CAPA** / **change** path.

---

*End of document*
