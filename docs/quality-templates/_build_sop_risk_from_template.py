"""Build SOP-Risk-Management-ISO14971.md from SOP-TEMPLATE-Risk-Management-ISO14971.md."""
from pathlib import Path

HERE = Path(__file__).parent
T = (HERE / "SOP-TEMPLATE-Risk-Management-ISO14971.md").read_text(encoding="utf-8")

T = T.replace(
    "<!--\n  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.\n  Replace every [BRACKET] placeholder before approval and obsoletes.\n-->\n\n# Risk Management for Medical Devices (ISO 14971:2019)\n",
    "<!--\n  SmartRisk / eQMS: Markdown with predictable ## headings for import as an editable SOP.\n  Replace every [BRACKET] placeholder before approval and obsoletes.\n  ISO 13485:2016 — application of risk in the QMS (e.g. 4.1.2, 7.1, 7.2, 7.3, 8.2, 8.4).\n  ISO 14971:2019 — application of risk management to medical devices.\n  Cross-references: DHF, DCR, record control, PMS, complaints, CAPA as applicable.\n-->\n\n# Medical Device Risk Management\n",
)
T = T.replace("**Risk Management for Medical Devices (ISO 14971:2019)**\n", "**Medical Device Risk Management (ISO 14971 / ISO 13485)**\n")
T = T.replace("*Shorter public title (optional):* [e.g., Risk Management Process]\n", "*Shorter public title (optional):* [Risk management / RMP and RMF]\n")
T = T.replace("**[SOP-XXX-##]**\n", "**[SOP-RM-##]** *(align to [Company] numbering convention [WI-XXX])*\n")
T = T.replace(
    "| **Supersedes** | [None / SOP-XXX-## Rev. n] |\n| **Document Owner** | [e.g., Director, Regulatory Affairs & Quality Assurance] |\n| **Planned review** | [Annual / on significant regulatory or product change] |\n| **Applicable standards** | ISO 13485:2016; ISO 14971:2019; [EU MDR 2017/745, UK MDR, 21 CFR 820, etc. as applicable] |\n\n---\n",
    "| **Supersedes** | [None / prior SOP number and version] |\n| **Document Owner** | [e.g., Director, Regulatory and Quality / Risk management lead] |\n| **Planned review** | [Annual / on significant regulatory change, serious event, or major QMS or product line change] |\n| **Applicable standards** | **ISO 14971:2019;** **ISO 13485:2016;** [EU MDR, IVDR, UK MDR, 21 CFR 820, IEC 60601, IEC 62304, IEC 62366, ISO 10993 as applicable] |\n| **Related SOPs** | [SOP-DC-##; SOP-RC-##; SOP for design and development; SOP for design change; SOP for PMS and complaint handling; SOP for CAPA] |\n\n---\n",
)
P3 = "\nThe process elements in this SOP, aligned with **ISO 14971:2019** and the QMS per **ISO 13485:2016** where they apply, are: **risk management planning,** **hazard identification,** **risk analysis,** **risk evaluation,** **risk control,** **residual risk assessment,** **benefit–risk analysis** when required, **risk management report,** **risk management review,** and **review of production and post-production information.**\n"
T = T.replace(" suitable for **notified body** and **regulatory** review.\n\n---\n", " suitable for **notified body** and **regulatory** review." + P3 + "\n---\n", 1)
T = T.replace("linked to **[SOP-XXX Design and Development]** and **[SOP-XXX Change Control]**", "linked to **[SOP-### Design and development]** and **[SOP-### Design and development changes]**", 1)
T = T.replace("meet **[SOP-XXX Document and Record Control]**", "meet **[SOP-DC-##]**, **[SOP-RC-##]**, and the electronic record policy, if any", 1)
T = T.replace("### Planning (ISO 14971, Clause 4)\n", "### Risk management planning (ISO 14971, 4.4; Clause 4)\n", 1)

old_anal = (
    "### Risk analysis and evaluation (Clauses 5 and 6)\n\n"
    "- Identify **reasonably foreseeable** hazards, sequences, and **harms** (including **[energy, chemical, biological, software, use error, misuse, lifecycle – as applicable]**).\n"
    "- **Estimate and evaluate** risk per RMP (e.g. **FMEA**, **FTA**, **matrix**).\n"
    "- Map unacceptable risks to **risk control** prior to **[design transfer / approval gate – define]** except where **documented** benefit–risk and regulatory requirements allow otherwise.\n"
)
new_anal = (
    "### Hazard identification, risk analysis, and risk evaluation (ISO 14971, Clauses 5 and 6)\n\n"
    "- **Hazard identification (e.g. 5.4):** identify **reasonably foreseeable** hazards, **hazardous situations,** sequences, and **harms** (including **[energy, chemical, biological, software, use error, misuse, lifecycle – as applicable]** as required by the RMP and **state of the art**).\n"
    "- **Risk analysis (5):** **estimate and evaluate** risk per RMP (e.g. **FMEA,** **FTA,** **matrix**); keep **trace** from hazards and risks to design **outputs,** **V&V,** and released **documentation** as required by the D&D plan and **[SOP-### Design and development]**.\n"
    "- **Risk evaluation (6):** compare to **risk acceptability** criteria; map unacceptable risks to **risk control** prior to **[design transfer / approval gate – define]** except where **documented** benefit–risk and regulatory requirements allow otherwise.\n"
)
T = T.replace(old_anal, new_anal, 1)

T = T.replace("### Residual risk and benefit–risk (Clauses 8 and 9)\n", "### Residual risk and benefit–risk (ISO 14971, 8, 8.2)\n", 1)

rmr = (
    "\n### Risk management report (ISO 14971)\n\n"
    "- The Organization shall document a **risk management report** in the RMF per the **RMP** and **[template DOC-###,]** "
    "summarizing the process, key outputs, **overall** residual **risk,** and, when the RMP or applicable regulation requires, a **benefit–risk** conclusion for the **intended use** (including a structured **benefit–risk analysis** when required in **[region / NB / technical file SOP – define]**).\n\n"
)
T = T.replace("### Risk management review (Clause 10)\n", rmr + "### Risk management review (Clause 9)\n", 1)
T = T.replace("### Production and post-production (Clause 11)\n", "### Production and post-production information (Clause 10)\n", 1)
T = T.replace("**[SOP-XXX Records]**", "**[SOP-RC-##]**", 1)
(HERE / "SOP-Risk-Management-ISO14971.md").write_text(T, encoding="utf-8")
print("Wrote", HERE / "SOP-Risk-Management-ISO14971.md")
