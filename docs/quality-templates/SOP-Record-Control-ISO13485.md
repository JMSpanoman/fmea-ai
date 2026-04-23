<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Clause 4.2.5 (Control of records).
  Cross-reference: SOP-Document-Control-ISO13485.md (controlled documents vs records).
-->

# Control of Quality Records

---

## Title

**Control of Quality Records**

*Shorter public title (optional):* [Record Control]

---

## SOP Number

**[SOP-RC-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Planned review** | [Annual / when retention rules or IT systems change] |
| **Applicable standards** | ISO 13485:2016 (4.2.5); [EU MDR 2017/745, IVDR 2017/746, UK MDR, 21 CFR 820, 21 CFR Part 11 as applicable] |
| **Related SOPs** | [SOP-DC-## Control of documents]; [SOP for electronic records / Part 11 if used] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **identifying, collecting, storing, protecting, retrieving, retaining, and disposing of** **quality records** in accordance with **ISO 13485:2016, clause 4.2.5**, so that records are **legible, readily identifiable, and retrievable** and support **medical device conformity**, **regulatory** obligations, and **notified body** review.

**Controlled documents** (procedures, instructions, blank forms) are managed per **[SOP-DC-##]**. This SOP applies to **records**: objective **evidence** that activities occurred or results were obtained, in **electronic**, **paper**, or **hybrid** form.

---

## Scope

### In scope

- **Quality records** for **[device classes / jurisdictions — list]**, including outputs from **design and development**, **production**, **purchasing**, **post-market** activities, **training**, **internal audit**, and **management review**, when required by the QMS, applicable regulations, or Organization procedures.
- The full record **lifecycle**: **creation**, **active storage**, **retrieval**, **retention**, and **disposition** (including **archive** vendors and **certified** destruction where used).
- Record categories in **Table A** (under Procedure) and any additional categories on **[DOC-### Record Retention Schedule]**.

### Out of scope

- [Pure business or HR records not used as QMS evidence — or state *none*.]
- [Attorney–client privileged materials — or state *none*.]

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **Top management** | Ensures resources for retention and retrieval; aware of implications of destruction and legal hold policies. |
| **Quality (record control owner)** | Maintains this SOP, the **record retention schedule**, index conventions, audit support, and centralized disposition approvals; coordinates with **IT** and **R&D** for electronic DHF/RMF stores. |
| **Process owners** (R&D, Operations, PMS, etc.) | Create complete, timely records; identify and classify per §2; do not delete or alter records inappropriately (§4). |
| **IT** | Access controls, backup and restore for electronic records, infrastructure suitability; supports Part 11–style controls where **[policy]** applies. |
| **All personnel** | Complete required records at the time of activity; use only authorized storage; report loss or corruption to **Quality** immediately. |

---

## Procedure

### Table A — Representative quality records (illustrative)

*Minimum retention periods and record owners are authoritative on **[DOC-### Record Retention Schedule]**.*

| Category | Examples (indicative) | Typical process owner for content |
|----------|------------------------|-----------------------------------|
| **Training** | Attendance, assessments, read-and-understand acknowledgments, role matrices | [Human Resources / Quality] |
| **Design and development (DHF)** | Design review minutes, design outputs, verification/validation protocols and reports, design transfer records | [R&D / Design Assurance] |
| **CAPA** | CAPA records, investigation, root cause, effectiveness verification, close-out | [Quality / CAPA owner] |
| **Complaints** | Complaint log entries, vigilance/regulatory reports, field correspondence (where not privileged per policy) | [Post-Market / Quality] |
| **Supplier** | Approved supplier list evidence, evaluations, audits, certificates of conformity, PO-linked acceptance records | [Supply Chain / Quality] |
| **Risk management (RMF)** | Risk management plan, analyses (e.g. FMEA), risk management report, review records, PMS-driven updates | [R&D / RAQA] |
| **Audit** | Internal audit program, checklists, findings, responses, effectiveness follow-up; management review outputs when stored as records | [Quality] |

*Add rows for sterilization batch records, calibration logs, DHR excerpts, or other QMS outputs as applicable.*

### 1. General principles (ISO 13485 4.2.5)

1.1 Quality records shall remain **legible** (durable paper; electronic formats readable over the required retention period), **readily identifiable** (linked to **device**, **batch**, **UDI** (DI/PI), **project**, or **complaint ID** as applicable), and **retrievable** within **[define — e.g. two business days for routine internal requests; shorter intervals where MDR/FDA vigilance timelines apply]**.

1.2 A quality record may be a completed form, protocol, log, report, data file, scanned image, or eQMS object. Email may be used only if permitted by **[WI-###]** and copied or indexed into the official record store.

### 2. Identification and index

2.1 Each record or record set shall include, where applicable:

- **Record type** (e.g. form number **FORM-##**).
- **Unique key** (e.g. project code, DMR reference, device identifier, lot/batch, complaint ID).
- **Date** (or date range) of the activity or decision.
- **Version** of the blank form or template used, if relevant to interpretation.
- **Originator** and **responsible party** (name or electronic user ID).

2.2 Filing structure in **[DMS / SharePoint / eQMS path]** shall follow **[Record Index Standard — DOC-###]** so that notified bodies and regulators can be oriented via **[Quality Manual addendum / training]**.

2.3 When systems change (e.g. new eQMS), a **record migration plan** shall preserve retrievability; validation shall be performed if **[GxP-relevant]** per **[VAL-### / SOP-DC-##]**.

### 3. Storage and active custody

3.1 Active records reside in **[defined locations / systems]**; access is **role-based** per **[access matrix]**. Production and R&D shall not use personal drives, consumer cloud accounts, or personal email as the **system of record** for quality data.

3.2 Off-site archive vendors shall have a **contract** defining physical and cyber security, **retrieval SLA**, and **destruction** at end of retention; vendor shall be listed on **[DOC-###]** or approved supplier records.

3.3 R&D or engineering **“not for manufacturing”** data shall not substitute for released **DHR** or commercial batch evidence without formal transfer per **[SOP-###]**.

### 4. Protection (integrity, confidentiality, backup)

4.1 **Integrity**

- **Electronic**: controlled check-in/check-out or equivalent; audit trails in **[LMS, eQMS, …]**; immutable or WORM storage where required by **[SOP-Part 11-###]**.
- **Paper**: chronological signatures; no intentional blank fields; permanent ink; error corrections per **[WI-###]** (single line strike, initialed and dated).
- **Corrections after the fact**: only with name, date, reason, and where applicable **change control** or **CAPA** reference; never to conceal nonconformities.

4.2 **Confidentiality** (PHI, patient-reported outcomes, sponsor data): per **[Data privacy / HIPAA policy]** or state **N/A**.

4.3 **Backup and disaster recovery**: backup **[frequency]**, restore tested **[frequency]**, RTO/RPO documented in **[IT disaster recovery plan]**.

4.4 **Unacceptable storage** includes unencrypted portable media for sensitive records, personal email without defined extraction to official store, and unapproved USB devices unless **[policy]** allows and encrypts.

### 5. Retrieval

5.1 Routine internal access is via **[DMS / eQMS]**. Non-routine reproduction requests may be logged in **[eQMS request / IT ticket]**.

5.2 For **notified body** reviews, **regulatory inspections**, **vigilance** responses, or **legal** requests, **Quality** (or designee) shall produce records or a **written statement of unavailability** with **CAPA** if records cannot be produced, within **[jurisdiction-specific timelines — define]**.

5.3 **Litigation or regulatory hold**: destruction is suspended per **[Legal + Quality policy]** and the **hold list**.

### 6. Retention and disposition

6.1 Minimum retention is defined on **[Record Retention Schedule — DOC-###]**, considering **product lifetime**, **customer contracts**, and **jurisdiction** (e.g. MDR/IVDR, UK MDR, FDA). Indicative examples (replace with your approved schedule):

- **Training**: [e.g. employment duration + two years, or per local rule].
- **Design (DHF)**: [e.g. commercial life + n years; align to MDR/IVD minimums where applicable].
- **CAPA and complaint (regulatory-reportable)**: [per MDR Annex, UK MDR, FDA — cite].
- **Supplier (critical to 4.1.1)**: [aligned with device records and NCR history].
- **Risk management (RMF)**: [aligned with DHF / device records].
- **Internal audit and management review**: [e.g. two full QMS cycles minimum, or life of device + five years — define].

6.2 No disposal of records tied to an **open CAPA**, **open vigilance file**, **FSCA**, or **suspected** serious incident without **QA and RA** joint check per **[WI-###]**.

6.3 At end of retention: **electronic** deletion or anonymized archive per **[IT SOP]**; **paper** secure shred with **certificate of destruction (CoD)** where required; **CoD** retained **[e.g. five years minimum]**.

6.4 **Indefinite hold** (litigation, M&A): **Quality** and **Legal** per **[policy]**.

### 7. Minimum expectations by record type

*Process SOPs and forms are the primary source; this subsection supports audits. See Table A.*

7.1 **Training records** — Unique person + training module/course ID; retraining dates; training content revision at time of completion (or LMS reference). Stored in **[LMS / path]**; retention per schedule.

7.2 **Design records** — Indexed to device/project; V&V linked to design inputs; changes under **[SOP-Change-###]**; per **[SOP-D&D-###]**.

7.3 **CAPA records** — Unique CAPA ID; full lifecycle from open to close; retained even when investigation concludes with no further action, if the investigation met procedure. Per **[SOP-CAPA-###]**.

7.4 **Complaint records** — Linked to vigilance/regulatory reporting decisions; PMS inputs; trend analysis references. Per **[SOP-Complaint-###]**.

7.5 **Supplier records** — Approval status; audits and certificates; evaluations (PPAP or simplified); linked to incoming inspection. Per **[SOP-Supplier-###]**.

7.6 **Risk management records** — Consolidated RMF or controlled eQMS view; post-production updates logged. Per **[SOP-Risk-###]**.

7.7 **Audit records** — Program, checklists, findings, responses, effectiveness; regulatory visit logs if used. Per **[SOP-Internal-Audit-###]**.

### 8. Cross-references

- **Controlled templates** vs **filled records**: [SOP-DC-##].
- **Electronic signatures** (e.g. US): [SOP-###].
- **Nonconformity, CAPA, complaint**: [SOP-###].

---

## Related Documents

| Document | Number |
|----------|--------|
| Control of documents and records (document portion) | [SOP-DC-##] |
| Record retention schedule (master) | [DOC-###] |
| Record index / file plan | [DOC-###] |
| IT access control | [POL-### / SOP-###] |
| Training management | [SOP-###] |
| Design and development (DHF) | [SOP-###] |
| CAPA | [SOP-###] |
| Complaint handling and vigilance | [SOP-###] |
| Supplier control | [SOP-###] |
| Risk management | [SOP-###] |
| Internal audit | [SOP-###] |
| Electronic records / 21 CFR Part 11 (if used) | [SOP-###] |

---

## Records

*This SOP is a controlled document. Examples of records demonstrating conformity to 4.2.5:*

| Record | Owner | Retention (indicative) | Location / index |
|--------|-------|------------------------|------------------|
| This SOP, revisions, approvals | Quality | [Per QMS document policy] | [eDMS] |
| Record retention schedule (DOC-###) and approved changes | Quality | [Life of QMS + n years] | [eDMS] |
| Record migration / major system cutover reports | Quality / IT | [Per retention schedule] | [eDMS / project folder] |
| Backup and restore test evidence (if not solely IT-owned) | IT / Quality | [Per IT policy] | [path] |
| Certificates of destruction (bulk disposition) | Designated approver | [e.g. minimum 5 years after destruction] | [secure storage] |

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
| Reviewed by (Quality) | | | |
| Reviewed by (R&D / Operations, as applicable) | | | |
| Reviewed by (IT, if e-records are centralized) | | | |
| Approved by (Management) | | | |

---

## Appendix A — ISO 13485:2016 mapping (informative)

| Theme | Clause | SOP sections |
|--------|--------|--------------|
| Control of records | 4.2.5 | All |
| Identification, storage, protection, retention | 4.2.5 (a) | §2, §3, §4, §6 |
| Retrievability | 4.2.5 (a) | §5 |

---

## Appendix B (optional) — Audit checklist

- [ ] Record retention schedule is approved, current, and applied.
- [ ] Sample records (training, DHF reference, CAPA, complaint, supplier, RMF, audit) are retrievable within the stated timeframe.
- [ ] Backup and restore (or DR exercise) documented per policy.
- [ ] No premature destruction (verify holds, open CAPA, vigilance, litigation).
- [ ] Personal drives and personal email are not the system of record for GxP data.

---

*End of document*
