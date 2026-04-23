<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Clause 7.3.4 (Design and development review).
-->

# Design Review

---

## Title

**Design Review**

*Shorter public title (optional):* [Design Review / DR]

---

## SOP Number

**[SOP-DR-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Planned review** | [Annual / when design control process or regulations change] |
| **Applicable standards** | ISO 13485:2016 (7.3.4); [21 CFR 820.30(e); MDR/IVDR design documentation expectations as applicable] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **planning, conducting, documenting, and following up** **formal design and development reviews** so that reviews occur at **suitable stages**, **deficiencies** are identified, **action items** are **tracked to closure**, and **objective evidence** supports **ISO 13485:2016, clause 7.3.4** and **notified body** expectations.

---

## Scope

### In scope

- **Formal design reviews** for **[medical devices / SaMD / accessories — define]** during **design and development** from **[concept through transfer — align with SOP-DDP-###]**, including **re-reviews** after **major changes**.
- **Planning** (when, who, independence), **agenda**, **minutes**, **decisions**, **action items**, **approvals**, and **closure** of open items before **stage exit** or **release** as defined in the **design plan** **[SOP-DDP-###]**.

### Out of scope

- [Informal engineering stand-ups without DHF record — or state *none*.]
- [Supplier-only reviews governed solely by supplier SOP — cross-ref **[SOP-Supplier-###]** if minutes are not DR minutes.]

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **D&D lead / project manager** | Schedules reviews per **design plan**; issues **agenda** and materials; tracks **action items** to **closure**; ensures **minutes** are filed in the **DHF**. |
| **Design Assurance / Quality** | Participates in all formal DRs; provides **independent** review or designates an **independent technical reviewer** per §3; may block stage exit if mandatory actions are open without an approved waiver. |
| **Chair** [role — e.g. engineering director] | Runs the meeting to time and agenda; documents **decisions** and **dissent** (if any). |
| **Participants** (per §2) | Prepare assigned sections; raise risks and gaps; accept or delegate action items as agreed. |
| **Regulatory / Clinical (as applicable)** | Contribute when agenda covers intended use, claims, labeling, clinical evaluation, or submission readiness. |

---

## Procedure

### 1. Review stages

1.1 Formal design reviews shall align with **gates** in the approved **design and development plan** **[SOP-DDP-###]** (e.g. after design inputs are approved, after design outputs before verification, pre-validation, pre-transfer, project closeout). Minimum reviews shall meet those gates unless a **documented risk-based consolidation** is approved by **Design Assurance**.

1.2 Hold **additional** triggered reviews when: (a) a **major design change** occurs; (b) **verification or validation** fails at a milestone; (c) **risk or usability** findings require re-baselining; or (d) a **notified body** or **internal audit** requires a focused review.

### 2. Participants

2.1 Each review shall have a **participant list** on the agenda (§5) including at minimum: **systems / lead engineer**, **Design Assurance** (or delegate), and **functional owners** for disciplines in scope (e.g. software, electrical, mechanical, human factors, and a **manufacturing representative** at transfer reviews).

2.2 **Regulatory** and **clinical** participants shall attend when the agenda includes intended use, labeling, clinical evaluation, or submission readiness.

2.3 Do not proceed without **critical** roles unless (a) **written** input was received before the meeting and is **read into minutes**, or (b) the meeting is **rescheduled** — document the choice in minutes.

### 3. Independence where appropriate

3.1 **Independent reviewer** means the person did **not** author the **primary** design artifact under review for that topic and has **no conflict of interest** that prevents objective judgment (define further in **[DOC-###]** if needed).

3.2 **Design Assurance / Quality** shall participate in **all** formal design reviews and may designate an **independent technical reviewer** for (a) verification protocol readiness, (b) risk-control implementation readiness, or (c) other **high-risk milestones** listed in **[DOC-###]**.

3.3 Where regulation or Company policy requires a **second signature** on V&V or risk documents, that rule is **in addition** to this SOP — see **[SOP-###]**.

### 4. Planning formal design reviews

4.1 At least **[n]** business days before the review, the D&D lead shall distribute an **agenda** (§5) and **pre-read package** (links to DIR, design outputs, risk summary, V&V status, open actions from prior DRs).

4.2 The review is not **formal** until the agenda and materials are under **configuration control** or stored in the **DHF** per **[SOP-DC-##]**.

### 5. Review agenda (minimum content)

Each formal design review agenda shall include:

- Review title, **stage / gate ID**, date, time, location (or video link).
- List of **participants** and roles; optional **observers** identified.
- **Objectives** of the review (what **pass** means for this gate).
- **Topics** in order (e.g. design inputs adequacy, outputs vs inputs, risk status, V&V readiness, labeling draft, manufacturing readiness).
- **References** to controlled documents and **revisions** under review.
- **Prior open action items** from the last DR with status.

### 6. Conducting the review

6.1 The **chair** follows the agenda; deviations are noted in minutes.

6.2 **Objective evidence** (tests, analyses, demos) may be presented; claims without evidence shall be recorded as **gaps** or **action items**.

6.3 **Decisions** shall be one of: (a) **Pass** the gate; (b) **Conditional pass** with listed actions due before the next dependent activity; (c) **Fail** — do not advance until re-review or plan update (§9).

### 7. Action items

7.1 Each action item shall have a **unique ID** (e.g. DR3-AI-07), **description**, **owner**, **due date**, and optionally **severity** or schedule risk if late.

7.2 Action items shall be entered in **[eQMS / Jira / minutes table — define]** and reflected in the **review minutes**.

7.3 Overdue actions without an approved extension shall escalate to **[D&D director and Design Assurance]** and may **block** subsequent gates.

### 8. Documentation requirements

8.1 Within **[n]** business days of the review, issue **approved minutes** containing at minimum:

- Attendance list or **e-sign roster** with roles.
- Summary of discussion by agenda topic (sufficient for an auditor to reconstruct decisions).
- Formal **decision** (pass / conditional / fail) and **rationale** if conditional or fail.
- Complete **action item** table (§7).
- List of **materials reviewed** (document IDs and revisions).

8.2 Minutes are **quality records** in the DHF per **[SOP-RC-##]**. Slides or handouts shall be **controlled attachments** or **summarized** in minutes so the DHF remains **audit-ready**.

### 9. Approval and closure of open items

9.1 Minutes shall be **approved** by **[Chair and Design Assurance — define]** before they are considered final.

9.2 **Conditional pass:** the gate is **closed** only when all **mandatory** actions are **verified closed** in the **[system of record]** and evidence is **linked or attached** to the minutes (or addendum).

9.3 **Fail / re-review:** update the **design plan** or schedule a follow-on DR; do not baseline dependent artifacts until the re-review **passes** or a **formal waiver** is approved by **[authority — define]**.

9.4 At project closeout, a summary shall confirm **zero open mandatory DR actions** or list **transferred owners** to sustaining with due dates.

---

## Related Documents

| Document | Number |
|----------|--------|
| Design and development planning | [SOP-DDP-###] |
| Design inputs | [SOP-DI-###] |
| Design and development (outputs, V&V, transfer) | [SOP-###] |
| Risk management | [SOP-Risk-###] |
| Change control | [SOP-###] |
| Control of documents | [SOP-DC-##] |
| Control of quality records | [SOP-RC-##] |
| CAPA (if DR actions escalate) | [SOP-###] |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Design review agenda and pre-read package | D&D lead | [Per DHF] | [eDHF / eQMS] |
| Approved design review minutes and attachments | D&D lead / Chair | [Per DHF] | [eDHF] |
| Action item register extract (if separate from minutes) | D&D lead | [Per DHF] | [eQMS] |
| Evidence of action closure linked to minutes | Action owners / QA | [Per DHF] | [eDHF] |

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
| Approved by (Management or D&D Director — define) | | | |

---

## Appendix A — ISO 13485:2016 mapping (informative)

| Clause | Expectation | This SOP |
|--------|-------------|----------|
| 7.3.4 | Planned reviews at suitable stages; identify deficiencies; propose necessary actions; record results | §1–§9 |
| 7.3.1 | Planning linkage | [SOP-DDP-###] |
| 4.2.5 | Records | [SOP-RC-##]; §8 |

---

## Appendix B (optional) — Audit checklist

- [ ] Design reviews scheduled per design plan gates; extra reviews triggered when required.
- [ ] Agendas and participant lists match minutes; critical roles not missing without documented substitute.
- [ ] Independence applied where policy requires (e.g. QA, independent technical reviewer).
- [ ] Decisions, action items (ID, owner, due date), and pass/conditional/fail are recorded.
- [ ] Minutes approved and filed in DHF; conditional items closed with evidence before dependent work.
- [ ] No open mandatory DR actions at closeout without approved transfer or waiver.

---

*End of document*
