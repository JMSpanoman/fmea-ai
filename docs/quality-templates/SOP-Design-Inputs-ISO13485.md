<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 13485:2016 — Clause 7.3.2 (Design and development inputs).
-->

# Design Inputs

---

## Title

**Design Inputs**

*Shorter public title (optional):* [Design Inputs / DIR]

---

## SOP Number

**[SOP-DI-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Planned review** | [Annual / when design control or standards change] |
| **Applicable standards** | ISO 13485:2016 (7.3.2); [ISO 14971:2019; IEC 62366-1; MDR/IVDR; 21 CFR 820.30(g) as applicable] |

---

## Purpose

To define **[Company Legal Name]** (“the Organization”) requirements for **identifying, documenting, reviewing, approving, and maintaining** **design inputs** for **medical devices** and related **accessories** or **software**, in accordance with **ISO 13485:2016, clause 7.3.2**, so that inputs are **complete, unambiguous, not conflicting**, suitable for **verification**, and **traceable** to **design outputs** and **risk management**.

---

## Scope

### In scope

- **Design inputs** for **[product types / project classes — define]** from initial definition through changes during D&D and, where applicable, post-transfer updates under **[SOP-Change-###]**.
- Categories in §3: **user needs**, **intended use**, **functional** and **performance** requirements, **regulatory**, **safety**, **usability**, and **traceability** per §8.
- The **Design Input Record (DIR)** or controlled equivalent and the **requirements / trace matrix** **[DOC-###]**.

### Out of scope

- [Marketing-only language not intended as verified design requirements — describe exclusion rule, or *none*.]
- [Non-DHF software or IT — or state *none*.]

---

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **Design Assurance / Quality** | Ensures process meets 7.3.2; participates in **review** and **approval**; supports **trace matrix** integrity and audits. |
| **R&D / Systems lead** | Leads identification and documentation of design inputs; resolves conflicts; owns the **DIR** in **[eQMS]**. |
| **Regulatory** | Regulatory, labeling, and IFU constraints as inputs; confirms jurisdiction requirements are captured. |
| **Clinical / Medical (if applicable)** | Clinical needs, contraindications, population constraints. |
| **Human factors / usability (if applicable)** | Usability-related inputs per **[SOP-### / IEC 62366-1]**. |
| **Risk management lead** | Aligns safety and risk-derived inputs with **RMP/RMF** per **[SOP-Risk-###]**. |
| **Operations (as applicable)** | Manufacturability, sterilization, servicing, and supply-chain constraints as inputs. |

---

## Procedure

### 1. General requirements (ISO 13485 7.3.2)

1.1 Design inputs shall be **determined** and **documented** in a controlled manner using a **Design Input Record (DIR)**, **[eQMS module]**, or equivalent under **[SOP-DC-##]**.

1.2 Design inputs shall be **reviewed** for adequacy (complete, clear, testable or otherwise verifiable as appropriate) and **approved** before they are relied upon as the basis for **design outputs** (per **[SOP-###]** and the **design plan** **[SOP-DDP-###]**).

1.3 **Conflicting** inputs shall be **resolved** and the resolution **recorded** before advancing design outputs that depend on them.

### 2. Identification and sources

2.1 The project team shall gather inputs from sources including at minimum:

- **User needs** — stakeholder interviews, market research, complaints, PMS data, competitive benchmarks.
- **Intended use** — indications, contraindications, patient/user population, use environment (from RA, clinical, product definition).
- **Applicable regulations and standards** — MDR/IVDR, FDA, IEC family, ISO 14971, IEC 62304, IEC 62366-1, etc.
- **Prior-generation or predicate** documentation where legally permitted.
- **Manufacturing and supply** constraints (design for X).
- **Risk management file** — hazards, risk controls, and safety-related needs from **[SOP-Risk-###]**.

2.2 Any source category **not applicable** shall be listed as **N/A** with **rationale** on the DIR cover sheet or in design review minutes.

### 3. Categories of design inputs (minimum content)

Each requirement shall have a **unique ID**, **statement**, and optionally **priority/criticality** and **owner** for clarification.

#### 3.1 User needs

Document what users and patients need the device to do or enable, in **user-oriented** language where helpful. User needs sit at the **top** of the validation trace chain (§8).

#### 3.2 Intended use

Document intended medical purpose, body site, duration of use, single vs multi-use, combination with other products, and limitations required by regulation or the clinical evaluation plan.

#### 3.3 Functional requirements

Document functions the device must perform (e.g. modes, algorithms, interfaces, data handling). Prefer **measurable** or **directly verifiable** statements.

#### 3.4 Performance requirements

Document quantitative limits (e.g. accuracy, response time, battery life, mechanical loads, environmental conditions) with **units** and reference to test conditions or linked specifications.

#### 3.5 Regulatory requirements

Document classification, essential principles / GSPR mapping intent, labeling and UDI constraints, MDR Annex I or FDA special controls as applicable, and any submission-bound statements under design control.

#### 3.6 Safety requirements

Document requirements from **risk management** (ISO 14971), including risk controls that become design constraints, alarm limits, electrical safety classes, software safety class per IEC 62304, and hazard mitigations not already captured under §3.3–3.4.

#### 3.7 Usability requirements

Document user interface requirements, use scenarios, known use errors to mitigate, training assumptions, and inputs to formative/summative success criteria per **IEC 62366-1** and **[SOP-###]**.

### 4. Documentation format and control

4.1 The DIR shall include or link to: **revision history**, **approvals** (or e-signatures), **effective date**, and a **list of referenced external documents** with revision level.

4.2 Each input row shall have a **stable identifier** (e.g. UR-01, DI-102). IDs shall not change for minor text clarifications; splits/mergers shall document supersession in revision history.

### 5. Review and approval

5.1 Hold a **design input review** at minimum before design outputs are **baselined** for verification (per gate in **[SOP-DDP-###]**) and again when a **major change** adds or modifies inputs.

5.2 Use a **review checklist** covering at minimum: (a) completeness vs intended use and applicable standards; (b) no unresolved conflicts; (c) verifiability for each input intended to be verified; (d) risk and usability coverage; (e) regulatory alignment.

5.3 **Approval** by **[R&D lead and Design Assurance — define]** shall be recorded in the DIR or linked meeting minutes.

### 6. Maintenance and changes

6.1 Changes to approved design inputs shall follow **[SOP-Change-###]** or the D&D change procedure during development, including **impact** on design outputs, V&V, risk file, and labeling.

6.2 Retired input IDs shall not be **reused** for new concepts within **[n]** years without **Quality** approval (or per **[WI-###]** naming rules).

### 7. Interface documents

- Design and development plan: **[SOP-DDP-###]**
- Risk management plan / RMF: **[SOP-Risk-###]**
- Usability engineering file: **[SOP-###]**
- Cybersecurity or software requirements document (if separate): **[SOP-###]**

### 8. Traceability expectations

8.1 Each design input ID shall appear in the **[requirements trace matrix — DOC-###]** mapped to one or more **design output** IDs (DO-###), **verification** method (test, analysis, inspection), and where applicable **validation** or **user need** ID.

8.2 Parent **user needs** may decompose to multiple technical design inputs; the matrix shall show **many-to-many** relationships explicitly.

8.3 Risk-control requirements shall trace to **hazard** IDs in the RMF and to **V&V** evidence per **[SOP-Risk-###]**.

8.4 The trace matrix is a **living controlled record**, updated through design reviews and at release readiness.

---

## Related Documents

| Document | Number |
|----------|--------|
| Design and development planning | [SOP-DDP-###] |
| Design and development (outputs, review, V&V, transfer) | [SOP-###] |
| Risk management | [SOP-Risk-###] |
| Change control | [SOP-###] |
| Control of documents | [SOP-DC-##] |
| Control of quality records | [SOP-RC-##] |
| Usability engineering | [SOP-### / IEC 62366-1] |
| Software lifecycle (if applicable) | [SOP-### / IEC 62304] |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Design input document (DIR) and revisions | R&D / Design Assurance | [Per DHF / product life + regulatory] | [eQMS / eDHF] |
| Design input review minutes / approvals | Design Assurance | [Per DHF] | [eDHF] |
| Requirements / trace matrix (or controlled extract) | R&D / Design Assurance | [Per DHF] | [eQMS] |
| Source material index (e.g. standards list, complaint excerpts) | R&D / RA | [Per DHF] | [eDHF] |

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
| Reviewed by (R&D / Systems) | | | |
| Reviewed by (Regulatory) | | | |
| Approved by (Management or D&D Director — define) | | | |

---

## Appendix A — ISO 13485:2016 mapping (informative)

| Clause | Expectation | This SOP |
|--------|-------------|----------|
| 7.3.2 | Design inputs determined, documented, reviewed, complete, unambiguous, not conflicting, verifiable | §1–§6 |
| 7.3.3–7.3.5 | Outputs, review, verification vs inputs | §8; execution in [SOP-###] |
| 4.2.4 / 4.2.5 | Document and record control | [SOP-DC-##], [SOP-RC-##] |

---

## Appendix B (optional) — Audit checklist

- [ ] Design inputs are documented, approved, and version-controlled before dependent design outputs are baselined.
- [ ] User needs, intended use, functional/performance, regulatory, safety, and usability categories are addressed or N/A with rationale.
- [ ] Conflicts were resolved with recorded decisions.
- [ ] Trace matrix links each design input ID to outputs and verification (and validation where applicable).
- [ ] Changes to inputs are controlled and impact risk, V&V, and labeling as needed.

---

*End of document*
