<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Clause 7.3.5 (Design and development verification).
-->

# Design Verification

---

## Title

**Design Verification**

*Shorter public title (optional):* [Design Verification / DV]

---

## SOP Number

**[SOP-DV-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Planned review** | [Annual / when V&V practice or applicable standards change] |
| **Applicable standards** | ISO 13485:2016 (7.3.5); [21 CFR 820.30(f); ISO 14971:2019 for risk-linked V&V; device-specific IECs as applicable] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **planning, executing, documenting, and approving** **design verification** to **confirm** that **design outputs** meet **design input** requirements, in accordance with **ISO 13485:2016, clause 7.3.5**. Design verification answers: **“Did we build the product right?”** (contrast with **validation**, which addresses **intended use** and is covered in **[SOP-###]**).

---

## Scope

### In scope

- **Verification** activities for **[medical devices, accessories, device software, SaMD — define]** at stages defined in the **design and development plan** **[SOP-DDP-###]** and the **V&V plan** **[VVP-###]**, including **re-verification** after **design changes** per **[SOP-Change-###]**.
- **Test planning**, **methods** (test, analysis, inspection, comparison), **protocols**, **acceptance criteria**, **objective evidence**, **traceability** to design inputs, **deviations**, and **verification reports** as **DHF** records per **[SOP-RC-##]**.

### Out of scope

- **Design validation** (user needs / clinical / simulated use) — **[SOP-###]**.
- **Incoming inspection** or **routine production** test — **[SOP-###]** unless **explicitly** identified as a **design verification** re-run for a **change**.

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **D&D lead / V&V lead** | Owns V&V planning and schedule; ensures **trace matrix** and **protocols** cover required design inputs. |
| **Test execution owners** | Run protocols per training and approved revisions; **document** **results** and **raw data**; initiate **deviations** when needed. |
| **Design Assurance / Quality** | Reviews/approves protocols and reports as defined; **independent review** where **§3** requires; approves **closure** of deviations affecting **conclusions**. |
| **Independent reviewer** (when required) | Confirms that methods, acceptance criteria, and conclusions are **defensible** without having been the sole author of the design under test (per §3). |
| **Regulatory (as applicable)** | **Awareness** of **submission-bound** test packages and **GLP**-like expectations if **[policy]** applies. |

---

## Procedure

### 1. General requirements (7.3.5)

1.1 **Design verification** shall be **planned** before execution (see §2) and **documented** so that each **design input** (or derived requirement) that will be **verified** has a defined **method**, **acceptance criteria**, and **objective evidence**.

1.2 Verification may use **examination, measurement, test, analysis, or inspection**, or **comparison** to a **known good** (predicate, gold device, or reference standard) when justified and **documented** in the protocol or report.

1.3 **Software and firmware** verification also follows **[SOP-### / IEC 62304]**. This SOP still governs **protocol/report** structure, **approvals**, and **DHF** records.

### 2. Test planning (verification at plan level)

2.1 The **V&V plan** **[VVP-###]** (or equivalent section in the D&D plan) shall state **which** design input (or requirement) IDs are **verified** by which **activity**, the **build/configuration** level, **test environment**, and which **residual risk controls** are re-checked, with **links to the RMF** per **[SOP-Risk-###]**.

2.2 **Statistical** methods (e.g. sampling, tolerance analysis) used for acceptance shall be **defined a priori** with **rationale** in the protocol or **[DOC-###]**.

2.3 **Test equipment, fixtures, and sites** used for verification shall be **qualified and/or calibrated** as required in **[SOP-### / WI-###]**.

### 3. Independent review (where appropriate)

3.1 **Protocol** and **final report** approval shall include **Design Assurance** (or delegate) who is not the **sole** author of the design outputs under test, unless a **formal second reviewer** is named per project policy.

3.2 For **highest criticality** verification (define in **[DOC-###]**, e.g. EMC, software OTS/SOUP integration, sterility), require **independent** sign-off by **[defined role]** in addition to the D&D owner.

### 4. Protocols and acceptance criteria

4.1 Prepare a **Design Verification (DV) protocol** using **[template DVP-###]** (or eQMS equivalent) for each **verification run** or **logical** group of related tests. Minimum content:

- Purpose and scope; link to **device/build/configuration ID** (hardware and software as applicable).
- **Design input** or requirement **IDs** covered.
- **Test articles** (quantity, lot, serial) and **rationale** if sample size is **less than** a full build.
- **Method** and test setup, including **equipment ID** and **calibration** or **qualification** reference.
- Step-by-step **procedure** or **link** to a controlled work instruction used in the test area.
- **Pre-defined acceptance criteria** (numeric where possible) and how **anomalies** are recorded.
- **Data** collection (forms, LIMS, DMS, photos, logs, automated files).
- **Roles** (executor, reviewer) and **approval** blocks.

4.2 **Protocol** revision and release per **[SOP-DC-##]**. Uncontrolled **drafts** are not used for regulated test execution (§8).

4.3 **Planned** protocol changes follow **D&D/change** control. **Unplanned** departures during execution are **deviations** (§6).

### 5. Methods and objective evidence

5.1 **Objective evidence** may include: calibrated **instrument** outputs, time-stamped **electronic** records, **photos** or **video** with **metadata**, **software logs**, automated test **exports**, and **signed** data forms.

5.2 State the **outcome** of each test or group as **pass**, **fail**, or **inconclusive** as defined in the protocol. **Do not** recast a **failed** run as **pass** without a **formal** deviation (§6) or **amended/approved** protocol.

5.3 **Retests** use a new execution record and/or a **new** or **revised** protocol version; **document** why a retest is **valid** (e.g. fixture error vs device defect).

### 6. Deviations and protocol changes during execution

6.1 A **deviation** is any **departure** from the **approved** protocol before or during the run, including to **test article, setup, sequence, or limits**.

6.2 Document unplanned deviations in **[FORM-###]** or a **controlled** lab **notebook** entry. **Design Assurance** assesses impact on the **validity** of results.

6.3 **Minor** deviations (e.g. **typo** in narrative with **no** effect on outcome): **log** and **conclude** in the report with **rationale**. **Major** deviations (affecting **acceptance** or **interpretation**): may require an **amended** protocol, **re-approval**, or **re-execution**; escalate to **CAPA** if a **root** design issue is indicated.

### 7. Traceability

7.1 Update the **requirements trace matrix** **[SOP-DI-###, DOC-###]** so that each design input (or **derived** requirement) row that is in scope for verification has: **(a)** protocol ID, **(b)** verification **report** ID, and **(c)** **conclusion** (Pass / **Fail** / N/A with **justification**).

7.2 If **one** design input is covered by **multiple** protocols, the **report** (or matrix) shall list all relevant protocol IDs.

7.3 Verification of **risk controls** also traces to **hazard** or **control** IDs in the RMF per **[SOP-Risk-###]**.

### 8. Execution discipline

8.1 Execute only against **approved, released** protocols in **[eDMS]**. The test area maintains **version** control awareness of the **active** protocol revision.

8.2 **Test** personnel meet **training** requirements per **[SOP-TR-##]** for the SOPs and WIs cited in the protocol.

8.3 Maintain **ALCOA+** data integrity: no pencil or **white-out** on permanent records; use **errata** per **[WI-###]**.

### 9. Verification report (or protocol + conclusion)

9.1 Each **verification** **report** (or a **conclusion** section in the **protocol** **package**) shall include at minimum:

- **Protocol** ID, **version**, and any **deviation** **ID**s.
- **Test** **article** and **environment** (date, location, **software** **version** as applicable).
- **Results** summary **tabulated** against **acceptance** criteria.
- **Conclusion** per **input** (or per protocol with a clear **matrix** link): pass / fail / N/A.
- Pointers to all **objective** evidence (appendix, file path, attachment).
- **Approved** signatories: **executor**; **optional** technical **peer**; **Design Assurance** or **QA** as **defined**.

9.2 **Fail** or **inconclusive** results do **not** set the **requirement** to **verified** in the **trace** **matrix** until **re-test**, **design** **change,** or a **formal** **waiver** (with **risk** and **regulatory** review as needed).

9.3 When all **in-scope** rows for a **milestone** are **verified**, a **design review** per **[SOP-DR-###]** may **record** **gate** **readiness** (see the **D&D** **plan**).

### 10. Design review linkage

- Do not declare **design verification** **complete** for a **regulatory** or **internal** **gate** without **review** of: **(a)** the **trace** **matrix, **(b)** key **reports,** and **(c)** any open **deviations,** per **[SOP-DR-###]**.

---

## Related Documents

| Document | Number |
|----------|--------|
| Design and development plan | [SOP-DDP-###] |
| Design inputs; trace matrix | [SOP-DI-###], [DOC-###] |
| Design review | [SOP-DR-###] |
| Design validation (complementary) | [SOP-###] |
| Risk management | [SOP-Risk-###] |
| Change control | [SOP-###] |
| Software lifecycle | [SOP-### / IEC 62304] |
| Control of documents | [SOP-DC-##] |
| Control of quality records | [SOP-RC-##] |
| Training and competency | [SOP-TR-##] |
| Calibrated equipment (test lab) | [SOP-###] |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| V&V plan (or D&D plan section) | D&D / V&V | [Per DHF] | [eDHF] |
| DV protocols and revisions | R&D / QA | [Per DHF] | [eDHF] |
| **Raw** data, logs, instrument outputs | Test lab / R&D | [Per DHF] | [controlled path] |
| Deviations / protocol amendments | QA / D&D | [Per DHF] | [eDHF] |
| **Verification** reports and approvals | R&D / QA | [Per DHF] | [eDHF] |
| **Updated** requirements trace matrix | D&D / QA | [Per DHF] | [eQMS] |

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
| Reviewed by (R&D / V&V) | | | |
| Approved by (Management or D&D Director — define) | | | |

---

## Appendix A — ISO 13485:2016 mapping (informative)

| Clause | Expectation | This SOP |
|--------|-------------|----------|
| 7.3.5 | Verification to ensure design outputs meet design input requirements, planned, documented, recorded | §1–10 |
| 7.3.2 | Design inputs (reference) | [SOP-DI-###] |
| 7.3.4 | Review | [SOP-DR-###] |
| 4.2.5 | Records of verification | [SOP-RC-##] |

---

## Appendix B (optional) — Audit checklist

- [ ] V&V or DV plan shows which inputs are verified, by which protocol, before execution.
- [ ] Protocols are approved, controlled, and match executed tests; deviations are assessed and closed.
- [ ] Acceptance criteria are pre-defined; objective evidence (raw data) is retrievable and tied to report conclusions.
- [ ] Trace matrix links each requirement to protocol, report, and pass/fail (or N/A with rationale).
- [ ] Independent review applied where required; failed results do not become “pass” without formal disposition.

---

*End of document*
