<!--
  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.
  Replace every [BRACKET] placeholder before approval and obsoletes.
  ISO 14971:2019 — hazard identification, hazardous situations, foreseeable sequences of events, harm.
  Cross-references: RMP, RMF, design and development, usability, software, labeling, record control.
-->

# Hazard Identification

---

## Title

**Hazard Identification (ISO 14971)**

*Shorter public title (optional):* [Hazard ID]

---

## SOP Number

**[SOP-HI-##]** *(align to [Company] numbering convention [WI-XXX])*

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
| **Planned review** | [Annual / when RMP, product line, or state of the art practice changes] |
| **Applicable standards** | **ISO 14971:2019;** [ISO 13485:2016; IEC 60601-1, IEC 62304, ISO 10993, IEC 62366-1; MDR, IVDR, 21 CFR 820 as applicable] |
| **Related SOPs** | [SOP-RM-## Risk management; SOP-### Design and development; SOP-### Software; SOP-### Usability; SOP-### Labeling/IFU; SOP-RC-##; SOP-DC-##] |

---

## Purpose

To define **[Company Legal Name]** ("the Organization") requirements for **hazard identification** in accordance with **ISO 14971:2019**, including identification of **reasonably foreseeable** **hazards**, **hazardous situations**, and **sequences of events** that can lead to **harm**, and for recording the results in the **risk management file (RMF)** in line with the **risk management plan (RMP)** and **[SOP-RM-##].**

Hazard identification shall be **planned**, **iterative**, and **traceable** across the product lifecycle, updated when the **RMP,** **intended use,** **applicable user profile,** **foreseeable misuse,** or **state of the art** changes, or when **post-production** information (complaints, vigilance, PMS) indicates new hazards or new hazardous situations.

---

## Scope

### In scope

- **Hazard and hazardous-situation identification** for **[medical device / IVD / SaMD / product family]** in **[UDI or family listing]** per the **RMP** and **intended use / indications for use.**
- Identification of **foreseeable sequences of events** from **(a)** initial **cause** or event (e.g. component failure, environmental stress, use step), through **(b)** a **hazardous situation** where people are exposed to a **hazard**, to **(c)** **harm**, per **ISO 14971:2019** and the RMP.
- **Normal** use and **fault** conditions, **user** and **use-error** (including **reasonably foreseeable misuse** as defined in the RMP), and interfaces with **usability, software, and labeling** activities.

### Out of scope

- Enterprise IT or business **risks** not related to **device** safety, unless the RMP explicitly extends scope (if **none,** state **none**).

**Justification** for out-of-scope items: **[RMP cover, quality plan, or RMF index].**

---

## Responsibilities

| Role | Responsibility |
|------|------------------|
| **Risk management lead (or program manager)** | Ensures the **RMP** requires **hazard identification** methods, inputs, and **review/approval** points; ensures updates when triggers in Section **Procedure** occur. |
| **Design and development (systems / mechanical / electrical / software)** | Contributes to **hazard** lists, **scenarios,** and **foreseeable** faults and failure modes; links to **design outputs** and V&V as required by the D&D plan. |
| **Usability / human factors** (as applicable) | Use-related **hazards,** tasks, and **foreseeable use errors**; alignment with **IEC 62366-1** where required. |
| **Software (SaMD / device software)** (as applicable) | Software / cybersecurity-related **hazardous situations** in line with **IEC 62304** and applicable security standards per RMP. |
| **Labeling / regulatory** (as applicable) | Inadequate information for safety, IFU, and off-label or ambiguous labeling scenarios per **RMP** and design inputs. |
| **Operations / service** (as applicable) | Installation, maintenance, and reprocessing (if any) as sources of **fault** and **hazardous situations** when in scope. |
| **PMS / complaints** | Feeds **post-market** data into re-identification and **RMP**-defined **reviews.** |
| **RAQA** | SOP compliance, RMF/record **integrity,** and audit readiness. |

---

## Procedure

### 1. Planning and context (RMP, ISO 14971 Clause 4)

- Hazard identification shall follow the **RMP** for the device or product family, including: **intended use,** user population, use environment, **applicable** consensus and regulatory standards, and **state of the art** (e.g. standards, **literature,** similar device experience, and external databases as defined in the RMP).
- The RMP shall name **hazard categories** the team must address (at minimum, the **categories in Subsection 6** below) and the **expected** work products in the RMF (e.g. **hazard analysis table,** **use scenarios,** **FMEA,** or equivalent).

### 2. Key concepts and identification logic (ISO 14971, Clause 5)

- **Hazard:** a **potential** source of harm. Record **hazard** descriptions so they are **unambiguous** and, where practicable, linked to a **hazardous characteristic** (e.g. **energy,** **substance,** **biological agent,** **incorrect** output) rather than to a single user slip only.
- **Hazardous situation:** circumstances in which **persons, property, or the environment** are **exposed** to one or more **hazards.**
- **Sequence of events:** a **credible** path from an **initiating** event (e.g. normal step, **fault,** or **use error**) through a **hazardous situation** to one or more **harms.** Multiple sequences may exist for a single **hazard.**
- **Foreseeable:** the team shall use **intended** use, **hazard** lists from standards and the **RMP,** and **usability** and **fault** analysis to determine what is **reasonably foreseeable,** and shall **document** assumptions in the RMF when needed for traceability and review.

### 3. Sources of hazards

- The organization shall systematically consider **sources** including, as applicable: **(a)** device **design** and technology (materials, energy, motion, software, data); **(b)** **manufacturing,** **installation,** **maintenance,** and **reprocessing;** **(c)** **environmental** and **emergency** context; **(d)** **user** and **use error**; **(e)** **foreseeable misuse;** **(f)** **interfaces** and **accessories,** and **(g)** information for safety, **IFU,** and **labeling.**
- Where the RMP references **similar** devices, **PMS,** or **literature,** the team shall extract **credible** new hazards and update the RMF.

### 4. Normal use and fault conditions

- For each relevant **operating** mode, identify **hazards** in **(a) normal** (including expected maintenance **when** in scope) and **(b) fault** and **abnormal** conditions, including: **component** or **subassembly** **failure,** **software** **faults,** out-of-**tolerance,** **environmental** stress, and **unintended** energy or substance release, as **defined** in the RMP and D&D plan.
- **Redundant** and **alarms,** and **failsafe** design where applicable, shall be considered when describing **scenarios,** not only when selecting **risk controls.**

### 5. User, use error, and foreseeable misuse

- Integrate with **usability** engineering: identify **hazardous** situations arising from **(a) task** and **(b) user interface** characteristics (e.g. ambiguous controls, error-prone steps, **workload,** and **inadequate feedback**), in line with **[SOP / plan for usability]** and **IEC 62366-1** where required.
- Treat **reasonably foreseeable** **use error** and, where the RMP requires, **intentional** or **improvised** **misuse** (e.g. off-label, inappropriate environment) as part of **sequence** and **hazard** identification, not as out-of-scope without **documented** **justification** in the RMF.

### 6. Categories of hazards (RMP and records)

- The RMF shall address **hazard** types relevant to the device, including the following as applicable, with **objective** descriptions that support **analysis** and **control:**

| Category | What to look for (non-exhaustive) |
|----------|----------------------------------|
| **Biological** | Reprocessing residues, **sterility** breach, **pyrogen,** pathogen, biocompatibility-related injury when applicable (**ISO 10993** in RMP) |
| **Chemical** | Reagents, leachables, cleaning agents, and toxic or corrosive **exposure** in **foreseeable** use |
| **Mechanical** | Trapping, cutting, **sharp** parts, instability, **parts** ejected, **wear** and **fracture** | 
| **Electrical** (including EMC where applicable) | Shock, **energy,** **fire,** and **emissions** in **normal and fault** conditions; **interference** with the device or other **equipment** when in scope | 
| **Software / programmable** systems | **Incorrect,** **delayed,** or **insecure** **behavior,** data corruption, and **unacceptable** user decisions driven by the software per **IEC 62304** as applicable | 
| **Usability** | Use errors and **hazardous** **situations** from **poor** **task** design, information architecture, and **perception/ cognition/ action** (see also Section 5) | 
| **Labeling / information for safety** | **Missing,** **wrong,** or **unclear** **indications,** **contraindications,** **warnings,** and **IFU** content leading to **hazardous** use | 

- The RMP may add **(e.g. thermal, radiation,** **cyber,** or **combination** product) categories for **state of the art**; document **rationale** if any standard category is **N/A** with a **conclusion** in the RMF.

### 7. Documentation in the RMF (traceability, ISO 14971 Clauses 4, 5)

- The RMF shall contain, or point to, **(a)** a **hazard-appropriate** list or tables with **hazards,** **hazardous situations,** and **scenarios,** and **(b)** **unambiguous** **links** to **hazard** IDs, **foreseeable** **harm,** and subsequent **analysis** and **control** (e.g. **FMEA,** risk table), per **RMP** templates and **[SOP-RM-##].**
- All **changes** to **hazards** or **scenarios** that affect **risk** shall go through the **applicable** **change** process and **D&D** plan and shall be **version-** and **date-** **controlled** per **[SOP-DC-##]** and **[SOP-RC-##].**

### 8. Review and approval

- **Hazard** identification **outputs** shall be **reviewed** at **RMP-** and **D&D-** defined **milestones** (e.g. design **inputs** approval, design **outputs** for risk, and **pre-release** **risk** review) by **competent** **persons** in **(at minimum):** design/relevant **technical** discipline(s), and **RAQA** or the **assigned** **risk** role. **Software** and **usability** leads **participate** when their **category** of **hazards** is in scope.
- A **formal** **record** of **review** and **approval** (electronic or signed as per the **Organization**’s policy) shall be **kept** in the **RMF** (or DHR/DMR reference, as defined by the RMP) and include **(a)** the **set** of **hazards** and **hazardous situations** **accepted** for the **milestone,** **(b)** any **open** **items,** and **(c)** **responsibilities** and **dates.**
- **Subsequent** **risk** **management** **review** and **re-identification** after market release follow **ISO 14971,** **Clause 9,** and **10** in **[SOP-RM-##].**

---

## Related Documents

| Document / template | Number | Use |
|---------------------|--------|-----|
| Risk management (RMP, RMF, process) | **[SOP-RM-##]** | Parent process and **reports** / **review** |
| Design and development | **[SOP-###]** | DHF, design **inputs/outputs,** and **V&V** link to **hazards** |
| Design change / change control | **[SOP-###]** | Changes affecting **hazard** set or **RMP** |
| Usability | **[SOP-###]** / IEC 62366-1 | **Use-** related **hazardous** situations and **scenarios** |
| Software (SaMD / embedded) | **[SOP-###]** / IEC 62304 | Software-**related** **hazards** and **faults** |
| Labeling and IFU | **[SOP-###]** | **Information** for **safety** and **labeling**-related **hazards** |
| Post-market, complaints, vigilance | **[SOP-###]** | **Post-production** **re-identification** inputs |
| Document and record control | **[SOP-DC-##, SOP-RC-##]** | **Controlled** RMF **documents** and **records** |
| RMP and hazard log templates | **[TMP-###, TMP-###]** | Prescribed **forms** in **eQMS** |

---

## Records

| Record | Owner | Retention | Location |
|--------|-------|-----------|----------|
| Hazard and hazardous-situation list / log (in RMF) | **[Risk / Eng.]** | **[Life of device + n years, per retention schedule]** | **RMF** / eQMS |
| Use scenarios, task analyses (if separate from RMF) | **[UE / D&D]** | [same] | RMF or DHF ref. |
| Review/approval of hazard ID at milestones | **[Risk Lead, RAQA]** | [same] | RMF |
| RMP changes reflecting hazard **scope** or **method** | **[Risk Lead]** | [same] | RMF |
| **Change** **records** for **hazard** updates | **[D&D or change owner]** | [same] | DHF / eQMS |

---

## Revision History

| Version | Date | Author | Description of change |
|---------|------|--------|------------------------|
| **[0.1]** | **[YYYY-MM-DD]** | **[##]** | **Initial** issue for review |
|  |  |  |  |
|  |  |  |  |

---

## Approval Signatures

*Obtain before **Effective Date**. E-signatures **allowed** if per **[SOP-### Electronic records / 21 CFR Part 11 policy].*

| Role | Name | Signature | Date |
|------|------|------------|------|
| **Prepared** by |  |  |  |
| **Reviewed** by (Quality) |  |  |  |
| **Reviewed** by (R&D / **Risk** **technical** lead) |  |  |  |
| **Approved** by (Management) |  |  |  |

---

## Appendix A — Informative: ISO 14971:2019 (illustrative) mapping to hazard identification (Clause 5)

| Topic | **ISO 14971:2019 (illustrative sub-clauses / annex)** | This SOP (illustrative) |
|-------|--------------------------------------------------------|------------------------|
| **Hazard** identification, **hazardous situations,** **scenarios,** **harm** | 5, **5.3**–**5.5,** Annexes **C, E, F, G, H,** **J** (as applicable) | **Sections 2, 3, 4, 5, 6, 7**; **RMP** |
| **Normal** and **fault** and **phenomena** (Annex) | e.g. **C.1** (categories), **C.2** (examples) | **Section 4**; **RMP** |
| **RMP,** **post-production,** **review** | 4, **4.2**–**4.4,** 9, 10 | **Sections 1, 7, 8;** **[SOP-RM-##]** |
| **Information** and **labeling** | 7, **5.2** and **5.3** in context of controls | **Sections 5, 6;** labeling **SOPs** |
| **Records and traceability** | 4, **3.2** (RMF), 9 | **Section 7;** **[SOP-RC-##]** |

*This table is **informative**; **applicable** regional and **notified body** expectations take precedence in **technical** documentation.*

---

## Appendix B (optional) — **Internal** audit or **gaps** check

- [ ] **Hazards** and **hazardous** **situations** are **unambiguous,** and **scenarios** link to **hazard** and **foreseeable** **harm.**
- [ ] **Normal** and **fault** and **(where** **RMP**-required) **misuse** and **use error** are **covered,** with **Rationale** for **N/A.**
- [ ] **Category** check (**biological** … **labeling**): **N/A** **justified** as needed.
- [ ] **RMP**-listed **standards,** **PMS,** and **state** of **art** are **reflected** in the **hazard** set.
- [ ] **Review** and **approval** at **RMP**-defined **milestones,** with **objective** **evidence** in the **RMF.**
- [ ] **Link** to **FMEA/ risk** table and **V&V** of **controls** (per **[SOP-RM-##]**).

---

*End of document*
