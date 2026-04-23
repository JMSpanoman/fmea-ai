<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Clause 4.2.4 (Control of documents). Quality records: see SOP-Record-Control-ISO13485.md (4.2.5).
-->

# Control of Documents

---

## Title

**Control of Documents**

*Shorter public title (optional):* [Document Control]

---

## SOP Number

**[SOP-DC-##]** *(example; align to [Company] numbering convention [WI-XXX])*

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
| **Document Owner** | [e.g., Director, Quality Assurance] |
| **Planned review** | [Annual / upon QMS or regulatory change] |
| **Applicable standards** | ISO 13485:2016 (4.2.3, 4.2.4); [21 CFR Part 11 if US e-records; EU MDR/IVDR document expectations as applicable] |

---

## Purpose

To establish **[Company Legal Name]** (“the Organization”) requirements for **creating, reviewing, approving, revising, distributing, accessing, and archiving** **controlled quality system documents** (policies, procedures, instructions, controlled blank forms, and applicable specifications) in accordance with **ISO 13485:2016, clauses 4.2.3 and 4.2.4**, so that only **approved, current** documents are used for **medical device** conformity, **regulatory** obligations, and **notified body** review.

**Quality records** (completed forms, logs, reports—objective evidence of activities) are identified, stored, retained, and disposed of per **[SOP-RC-## Control of quality records]**. This SOP may reference **record** identification where the same media (electronic or paper) carries both **document** and **record** rules. The Organization uses **[electronic, paper, or hybrid]** media as defined below.

---

## Scope

### In scope

- All **controlled QMS documents** for **medical device** activities: **policies**, **SOPs**, **work instructions (WIs)**, **controlled blank forms/templates**, **drawings** and specifications under QMS, **labeling** masters if controlled here, and **external** documents recognized as QMS inputs.
- **Master** documents, **controlled copies** (where used), **obsolete** document handling, and **archived** superseded **document** revisions in **[list sites / functions]**.
- **Electronic** and **paper** **document** media, including **access**, **version** state, and **backup** of **released** **document** repositories.

### Records (cross-reference)

- Filled forms, batch records, and other **quality records** are in scope of **[SOP-RC-##]**; this SOP addresses only **blank** **controlled** **forms** as **documents** until completed.

### Out of scope

- [**Business-only** documents (e.g. HR handbooks) not used for QMS — or state “none if all sites use one DMS”].
- [ **Uncontrolled** reference material — define, e.g., public standards kept for information only, not edited by the Organization].

Exclusions, if any, are **listed in [DOC-XXX] Document Master List** or **eQMS metadata** with **justification**.

---

## Responsibilities

| Role | Responsibility |
|------|------------------|
| **Top management** | Ensures QMS includes documented procedures for **document** control; approves **quality policy** and other documents per **[Company] approval matrix [DOC-XXX]**. |
| **Document Control / Quality** | Maintains this SOP, **numbering** rules, **master list** or eQMS structure, **training** on DMS, and support for **audits**; coordinates **obsolete** handling and **document** **archive** rules. |
| **Document owner / process owner** | **Authors** or delegates drafting; initiates **review and revision**; ensures **content** is correct for the process. |
| **Reviewers** | **Technical and quality** review per **approval matrix**; confirm accuracy, legality, and QMS fit. |
| **Approvers** | **Authorized** signatories (or e-signatures) per **matrix**; **no use** of **unapproved** documents for GMP decisions. |
| **IT / system owner** | **Access controls**, **backup**, **system validation** state (as applicable to **[eQMS / DMS name]**); supports availability and integrity of **released** **electronic** **documents**. |
| **All personnel** | Use **only current, approved** documents for regulated work; complete **records** per process SOPs; do **not** use **obsolete** controlled copies. |

---

## Procedure

### 1. Document types and classification

1.1 The Organization classifies QMS documentation at minimum as follows (adjust labels to match **[Document Master List]**):

| Type | Description | Example prefix / code |
|------|-------------|------------------------|
| [POL] | Policy | [POL-##] |
| [SOP] | Standard operating procedure | [SOP-XX-##] |
| [WI] | Work instruction | [WI-XX-##] |
| [FORM] | Controlled form / template | [FORM-##] |
| [SPEC] | Design / product specification (if under this procedure) | [as defined] |

1.2 **External documents** (e.g. **ISO** standards, **regulations**) used as **input** to the QMS shall be **listed** in **[master list / library]** with **title, revision, source, and date** of recognition; **supersession** of internal procedures shall not rely on unlisted external versions.

### 2. Document numbering and identification

2.1 Each **controlled** document shall carry a **unique** identifier per **[DOC-XXX Document Numbering and Naming]**:

- **Document number** (fixed for the life of the document; does not change at revision in schemes where **revision** is tracked separately).
- **Title**.
- **Revision** or **version** level (e.g. **0.0** draft, **1.0** first release, **1.1, 2.0** per revision rules in §3).
- **Effective date** (date of **approval** for that revision).
- **Status**: **Draft**, **Approved (controlled)**, or **Obsolete** (or equivalent in eQMS).
- **Page** **x of y** (for multi-page **paper** masters if used).

2.2 **Records** (outputs of a process) shall be identified by **record type** (e.g. form number), **project/batch/UDI** or **other trace key**, and **date**, per the applicable SOP or form, so that records are **unambiguous** and **retrievable**.

2.3 **Prohibited**: reusing a **retired** document number for a **new** document within **[n]** years, unless **documented** exception in **[DMS or QA log]**.

### 3. Version control and revision

3.1 **Revision** increments when **content** changes; **format-only** (e.g. typo) changes may be **[Minor vs. Major]** per table:

| Change impact | Example revision step |
|--------------|------------------------|
| **Major** (process, responsibility, or regulatory effect) | **[1.0 → 2.0]** |
| **Minor** (clarification, no behavior change) | **[1.0 → 1.1]** |
| **Editorial** (as allowed by policy) | **[1.0 → 1.0.1 or same with errata log]** |

*[Define table to match eQMS capabilities.]*

3.2 The **only** **approved** “current” version is the one **released** in **[eQMS / DMS]**, **published** in **[intranet]**, and/or the **stamped** **paper** master at **[location]**, as applicable.

3.3 **Working drafts** shall be stored in **[designated DMS area / prefix “DRAFT-”]** and shall be **unusable** for production or release decisions until **approved** per §4.

3.4 **Change history** (summary of what changed) shall be in the document’s **revision history** section and/or **eQMS** audit trail, **before** or **at** each approval.

### 4. Document creation, review, and approval before release

4.1 **Authoring**: The **document owner** (or designee) prepares or updates content using **[template TMP-XXX]** for SOPs/WIs.

4.2 **Review**: **Minimum** reviewers: **[Quality]** and **[(subject-matter) process owner]**. **Regulatory** review for **[labeling, submission-bound, or MDR/IVD-regulated text — define]**.

4.3 **Approval**: **Approvers** are per **[Document Approval Matrix — DOC-XXX]**; **no document** is **effective** for regulated use without **all required** approvals and **Effective Date** assignment.

4.4 **Release** actions:

- **Electronic**: set status to **Released**; **obsolete** prior revision; **propagate** **notification** (e.g. eQMS, email) to **affected** roles and the **training** queue (§8); ensure **read-only** access to **old** rev for **[defined period]** if needed for audit, then **archive** per §7.
- **Paper** (if used): issue **revised** **master**; mark prior master **obsolete**; collect **uncontrolled** copies for destruction or stamp **“Obsolete — for reference only”** per **QM**; update **log** of **distributed** controlled copies (§5).

4.5 **Uncontrolled** documents (e.g. vendor brochures) are **permitted** only in a **[read-only reference library, not the controlled procedure index]**; they shall **not** be marked as **Company** **approved** procedures.

### 5. Distribution and access to current versions

5.1 **Authorized** users shall have **read** access to **current** QMS documents via **[DMS / SmartRisk / network path]**. **Write** and **release** access is limited to **named** roles in **[DMS groups / access matrix]**.

5.2 **Printouts** of controlled procedures are **uncontrolled** unless **issued** as a **stamped** **controlled copy**; **stamping** and **reconciliation** follow **[WI-DC-##]** if the Organization uses **floor** **paper** copies.

5.3 **Records** of **where** a document applies (e.g. **applicable process sites**) are maintained in **[Document Master List]** to support **retrieval** and **update** of **affected** personnel in **revisions**.

### 6. Obsolete document handling

6.1 A document becomes **obsolete** when: **(a)** superseded by a **new** revision, **(b)** procedure is **retired** (e.g. process eliminated), or **(c)** **regulatory** withdrawal of a required doc type.

6.2 **Obsolete** **electronic** files: status = **Obsolete**; not in **“current”** search; **read-only** **archive** available to **[RAQA, audit]** for **retention** **period**; **watermark** or banner **“Obsolete”** for any **intentional** viewing of old rev.

6.3 **Obsolete** **paper**: remove from **use**; **deface** (e.g. “OBSOLETE” stamp) or **segregate**; **log** **destruction** of unneeded copies per **[policy]**; keep **at least one** **archival** **copy** of the **last** **superseded** **revision** in **[file room / e-archive]** **unless** the **eQMS** **replaces** **entire** **set**.

6.4 **Labels** and **IFU** **obsolete** handling, if not fully under this SOP, is cross-referenced to **[SOP-Labeling-##]**.

### 6.5 Archiving of superseded document revisions

6.5.1 **Superseded** (obsolete) **document** revisions shall remain **retrievable** for **[minimum period — e.g. two full revision cycles, life of related product file, or QMS lifetime + n years]** in a **read-only** **archive** (eQMS archive library, or segregated paper archive) for **notified body** and **internal** **audit** traceability, unless **regulation** or **[Record / document archive policy]** requires longer retention.

6.5.2 **Archive** **index** shall include **document number**, **revision**, **obsolete** **date**, and **superseded-by** **revision** **reference**.

### 7. Interface to quality records (ISO 13485 4.2.5)

7.1 **Completed** forms, logs, and reports are **quality records**, not **controlled documents**. They are **identified, stored, protected, retrieved, retained, and disposed of** per **[SOP-RC-##]** and the **[Record Retention Schedule — DOC-XXX]**.

7.2 **Blank** controlled **forms** remain under **this** SOP until issued for use; the **form number** and **revision** on the **blank** shall match the **released** **document** in the DMS.

7.3 **Corrections** to **records** after the fact: per **[SOP-RC-##]** and **[WI-###]**; do not circumvent **record** integrity rules when revising **procedures** that define those records.

### 8. Training and communication of changes

8.1 When a **document** is **revised** in a way that **affects** how work is **performed**, **affected** personnel are **trained** (or **read-and-understand** with **acknowledgment** per **Company** policy) **before** or **within** **[X business days of effective date]**, and **evidence** is in **[LMS / training matrix]**.

8.2 **Acknowledgment** in **[eQMS]** may **substitute** for **separate** **sign-off** if **validated**.

### 9. Electronic and paper media

9.1 **Electronic** **controlled documents** shall:

- Reside in **[validated eQMS / DMS]**, or on **shares** only with **[path rules]** and **document** **version** **control**;
- **Restrict** access by **role**; **unique** user IDs; **time-stamped** **audit trail** for **create, change, release, obsolete**;
- **Backup** **[frequency]**, **restore** **tested** **[frequency]**;
- If U.S. FDA **21 CFR Part 11** applies to the DMS: **[closed system controls, e-signatures, validation package ref. VAL-XXX]**.

9.2 **Paper** **document** **masters** shall:

- **Physical** **security** at **[location]**;
- **Controlled** **issuance** of **reprints**; **reconciliation** of **obsolete** copies per **[WI-DC-##]**;
- **Scanning** masters to **electronic** **archive** is **permitted** when **[WI-DC-##]** and **validation** (if required) are **met**.

9.3 Where **electronic** and **paper** **both** exist for the **same** **controlled** **document**, one shall be defined as the **master (system of record)** in **[Document Master List]** or the DMS metadata.

9.4 **Electronic** and **paper** **quality records** (not blank forms): per **[SOP-RC-##]**.

### 10. Interactions with other QMS elements

- **Change control** of design or process documents: **[SOP-XXX Change Control]**.  
- **Supplier-provided** documentation: **[SOP-XXX]**.  
- **CAPA** if document failures require correction: **[SOP-XXX]**.  

---

## Related Documents

| Document | Number | Notes |
|----------|--------|--------|
| Quality manual | [QM-001] | QMS scope |
| **Control of quality records** | [SOP-RC-##] | 4.2.5; full record lifecycle |
| Document / form numbering and naming | [WI-### or SOP] | Tied to §2 |
| Document approval matrix | [DOC-###] | Tied to §4 |
| Record retention schedule | [DOC-###] | Tied to §7; owned per SOP-RC |
| **Training** on document changes | [SOP-###] | Tied to §8 |
| Electronic records & signatures (if US) | [SOP-###] | Tied to §9 |
| Labeling / IFU control (if separate) | [SOP-###] | Tied to §6 |

---

## Records

| Record | Owner | Retention | Index / location |
|--------|-------|------------|------------------|
| **Master** document and **revision** **history** | Document Control / Owner | [Life of QMS + n years] | [eQMS] |
| **Document** **approval** **(release)** **evidence** | Quality | [same] | [eQMS] |
| **List** of **current** and **obsolete** (or eQMS report) | Document Control | [current + archive] | [DMS] |
| **Distribution** or **acknowledgment** of **revisions** | [QA / LMS] | [per training policy] | [LMS] |
| **Record** **retention** and **destruction** **logs** | Quality | [per schedule + audit] | [path] |
| **Backup** and **restore** test records (e-systems) | IT / QA | [per IT policy] | [path] |

---

## Revision History

| Version | Date | Author | Description of change |
|---------|------|--------|------------------------|
| [0.1] | [YYYY-MM-DD] | [##] | Initial issue for review |
| | | | |

---

## Approval Signatures

*Obtain before **Effective Date**. Electronic signatures per **[SOP-###]** if used.*

| Role | Name | Signature | Date |
|------|------|------------|------|
| Prepared by | | | |
| Reviewed by (Quality) | | | |
| Reviewed by (IT / e-records, if applicable) | | | |
| Approved by (Management) | | | |

---

## Appendix A — Mapping to ISO 13485:2016 (informative)

| Topic | Clause | This SOP (section) |
|--------|--------|---------------------|
| QMS documentation | 4.2.3, 4.2.4 | §1–6, §8–9; §6.5 archive |
| Control of records | 4.2.5 | §7 (interface); primary: [SOP-RC-##] |

---

## Appendix B (optional) — Quick audit line items

- [ ] Only **released** documents in work areas (eQMS “current” view and/or stamped paper masters).
- [ ] **Numbering** is unique; **revisions** are traceable; **obsolete** documents are segregated, watermarked, or access-restricted.
- [ ] **Approvals** are complete before **Effective Date** for regulated use.
- [ ] **Superseded document** revisions are **archived** and indexed per §6.5.
- [ ] **Quality records** meet **[SOP-RC-##]** (retention, backup, retrieval).
- [ ] **Training** or read-and-understand on applicable procedure changes per §8.

---

*End of document*
