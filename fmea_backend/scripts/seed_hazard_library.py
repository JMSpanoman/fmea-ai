"""
Seed hazard_library with 150+ medical device hazards across 10 categories.
Run from repo root: python -m fmea_backend.scripts.seed_hazard_library
Or from fmea_backend: python scripts/seed_hazard_library.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.hazard_library import HazardLibrary

REF = "ISO 14971, IEC 62471, IEC 60601-1"

HAZARDS = [
    # --- ELECTRICAL (15) ---
    {"code": "HZ-E01", "name": "Electric shock from accessible live parts", "description": "User or patient contact with live electrical parts due to insulation failure or enclosure breach.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E02", "name": "Leakage current exceeding safe limits", "description": "Touch or patient leakage current above applicable limits (e.g. IEC 60601-1).", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E03", "name": "Short circuit or overload", "description": "Internal short circuit or overload leading to overheating, fire, or loss of function.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E04", "name": "Electromagnetic interference (EMI)", "description": "Device emissions or susceptibility affecting itself or other equipment.", "category": "electrical", "source_standard": "IEC 60601-1-2"},
    {"code": "HZ-E05", "name": "Electrostatic discharge (ESD) damage", "description": "ESD causing latent or immediate failure of electronic components.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E06", "name": "Incorrect or unstable mains voltage", "description": "Operation outside specified voltage range causing malfunction or damage.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E07", "name": "Battery explosion or leakage", "description": "Thermal runaway, leakage, or rupture of batteries.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E08", "name": "Ground fault or loss of protective earth", "description": "Loss of protective earth connection increasing shock risk.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E09", "name": "Arc or spark in flammable atmosphere", "description": "Electrical arcing or sparking in oxygen-enriched or flammable environment.", "category": "electrical", "source_standard": "IEC 60601-1"},
    {"code": "HZ-E10", "name": "Inadvertent activation from power surge", "description": "Power surge or transient causing unintended device activation.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E11", "name": "Capacitor or component failure", "description": "Failure of capacitors or critical components leading to loss of safety function.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E12", "name": "Incorrect polarity or wiring", "description": "Reverse polarity or miswiring causing malfunction or hazard.", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E13", "name": "Induced voltage on patient-connected parts", "description": "Unintended voltage on applied parts from magnetic or capacitive coupling.", "category": "electrical", "source_standard": "IEC 60601-1"},
    {"code": "HZ-E14", "name": "Overcurrent to patient tissue", "description": "Excessive current delivered to patient (e.g. from therapeutic or monitoring circuit).", "category": "electrical", "source_standard": REF},
    {"code": "HZ-E15", "name": "Failure of electrical isolation", "description": "Breakdown of isolation between mains and patient/applied parts.", "category": "electrical", "source_standard": REF},
    # --- MECHANICAL (16) ---
    {"code": "HZ-M01", "name": "Sharp edges or burrs", "description": "Exposed sharp edges or burrs causing cuts or puncture.", "category": "mechanical", "source_standard": "ISO 14971, IEC 60601-1"},
    {"code": "HZ-M02", "name": "Pinch or crush point", "description": "Moving parts or closure creating pinch or crush hazard.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M03", "name": "Falling or dropped device", "description": "Device falling onto patient or user due to instability or mounting failure.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M04", "name": "Fragmentation or breakage", "description": "Part breaking or fragmenting during use (e.g. glass, plastic, mechanism).", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M05", "name": "Entanglement with moving parts", "description": "Hair, clothing, or tubing entangled in rotating or moving parts.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M06", "name": "Inadvertent release of spring-loaded mechanism", "description": "Unexpected release of stored mechanical energy.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M07", "name": "Catheter or needle breakage", "description": "Breakage of catheter, needle, or cannula in vivo.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M08", "name": "Detachment of implant or component", "description": "Implant or internal component detaching or migrating.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M09", "name": "Excessive force or pressure", "description": "Mechanical force or pressure beyond safe limits on tissue or structure.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M10", "name": "Wear or fatigue failure", "description": "Failure due to wear, fatigue, or cyclic loading.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M11", "name": "Incorrect assembly or alignment", "description": "Misassembly or misalignment causing malfunction or injury.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M12", "name": "Protrusion or snag hazard", "description": "Protruding parts causing snagging or trauma.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M13", "name": "Loose or detached small parts", "description": "Small parts (e.g. screws, caps) becoming loose and aspirated or lost in wound.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M14", "name": "Inadequate structural integrity", "description": "Housing or support failing under normal or foreseeable use.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M15", "name": "Overpressure in fluid path", "description": "Excessive pressure in tubing or fluid path causing rupture or embolism risk.", "category": "mechanical", "source_standard": REF},
    {"code": "HZ-M16", "name": "Mechanical obstruction or occlusion", "description": "Obstruction of flow path or moving part leading to malfunction or injury.", "category": "mechanical", "source_standard": REF},
    # --- THERMAL (15) ---
    {"code": "HZ-T01", "name": "Burns from hot surfaces", "description": "User or patient contact with surfaces exceeding safe temperature limits.", "category": "thermal", "source_standard": "IEC 60601-1"},
    {"code": "HZ-T02", "name": "Overheating of device or battery", "description": "Internal overheating leading to burn, fire, or failure.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T03", "name": "Cryogenic or cold burn", "description": "Tissue damage from contact with very cold surfaces or cryogen.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T04", "name": "Thermal runaway", "description": "Uncontrolled temperature rise (e.g. battery or heater).", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T05", "name": "Fire or ignition", "description": "Ignition of device materials or surrounding atmosphere.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T06", "name": "Inadequate thermal insulation", "description": "Heat or cold transfer to user/patient beyond design intent.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T07", "name": "Hot fluid or steam release", "description": "Release of hot liquid or steam causing scalding.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T08", "name": "Laser or optical radiation burn", "description": "Tissue damage from optical or laser radiation.", "category": "thermal", "source_standard": "IEC 60601-2-22, IEC 62471"},
    {"code": "HZ-T09", "name": "RF or microwave heating", "description": "Tissue heating from RF or microwave energy (intended or stray).", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T10", "name": "Exothermic reaction", "description": "Unintended exothermic chemical or battery reaction.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T11", "name": "Ambient temperature out of range", "description": "Device used or stored outside specified temperature range.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T12", "name": "Heat sink or cooling failure", "description": "Loss of cooling leading to overheating of components.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T13", "name": "Thermal shock to materials", "description": "Rapid temperature change causing material failure or leakage.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T14", "name": "Excessive ablation or coagulation", "description": "Over-delivery of thermal energy to tissue.", "category": "thermal", "source_standard": REF},
    {"code": "HZ-T15", "name": "Hot exhaust or vent", "description": "Hot air or gas from vents causing burn or discomfort.", "category": "thermal", "source_standard": REF},
    # --- SOFTWARE (16) ---
    {"code": "HZ-S01", "name": "Incorrect or stale data display", "description": "Display showing wrong, outdated, or misleading information.", "category": "software", "source_standard": "IEC 62304, ISO 14971"},
    {"code": "HZ-S02", "name": "Software crash or hang", "description": "Unhandled exception or deadlock causing loss of function.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S03", "name": "Incorrect algorithm or calculation", "description": "Wrong formula or logic leading to incorrect dose, setting, or result.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S04", "name": "Race condition or timing fault", "description": "Concurrency or timing error causing unpredictable behavior.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S05", "name": "Incorrect unit or scale", "description": "Wrong unit (e.g. mg vs µg) or scale causing overdose or misinterpretation.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S06", "name": "Unintended activation or deactivation", "description": "Feature activating or deactivating without user intent.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S07", "name": "Loss of configuration or calibration", "description": "Stored settings or calibration lost (e.g. after power cycle).", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S08", "name": "Incorrect patient or data association", "description": "Data linked to wrong patient or episode.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S09", "name": "Buffer overflow or memory fault", "description": "Memory corruption leading to crash or unsafe state.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S10", "name": "Inadequate input validation", "description": "Invalid or malicious input causing error or unsafe behavior.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S11", "name": "Firmware or software update failure", "description": "Failed or partial update leaving device in inconsistent state.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S12", "name": "Incorrect sequence of operations", "description": "Allowed or forced sequence that leads to hazard (e.g. bypassing checks).", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S13", "name": "Inadequate alarm or alert", "description": "Missing, delayed, or incorrect alarm for hazardous condition.", "category": "software", "source_standard": "IEC 60601-1-8, IEC 62304"},
    {"code": "HZ-S14", "name": "Date/time or timezone error", "description": "Incorrect date, time, or timezone affecting therapy or records.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S15", "name": "Default or fallback to unsafe value", "description": "Fallback to a default that is unsafe in some use case.", "category": "software", "source_standard": "IEC 62304"},
    {"code": "HZ-S16", "name": "Incorrect mode or state transition", "description": "Device entering wrong mode or state (e.g. therapy when intended standby).", "category": "software", "source_standard": "IEC 62304"},
    # --- BIOLOGICAL (15) ---
    {"code": "HZ-B01", "name": "Biocompatibility reaction", "description": "Adverse tissue reaction to materials (cytotoxicity, sensitization, etc.).", "category": "biological", "source_standard": "ISO 10993, ISO 14971"},
    {"code": "HZ-B02", "name": "Pyrogenic response", "description": "Febrile or inflammatory response to pyrogens or endotoxins.", "category": "biological", "source_standard": "ISO 10993"},
    {"code": "HZ-B03", "name": "Infection or contamination", "description": "Introduction or spread of pathogenic organisms.", "category": "biological", "source_standard": "ISO 14971"},
    {"code": "HZ-B04", "name": "Transmission of infectious agent", "description": "Device as vector for transmission (e.g. bloodborne, respiratory).", "category": "biological", "source_standard": "ISO 14971"},
    {"code": "HZ-B05", "name": "Allergic or hypersensitivity reaction", "description": "Allergic reaction to device materials or residues.", "category": "biological", "source_standard": "ISO 10993"},
    {"code": "HZ-B06", "name": "Toxic or leachable substance", "description": "Release of toxic or harmful leachables from materials.", "category": "biological", "source_standard": "ISO 10993"},
    {"code": "HZ-B07", "name": "Endotoxin exposure", "description": "Exposure to bacterial endotoxins above safe limits.", "category": "biological", "source_standard": "ISO 10993"},
    {"code": "HZ-B08", "name": "Cross-contamination between patients", "description": "Transfer of biological material between patients via reusable device.", "category": "biological", "source_standard": "ISO 14971"},
    {"code": "HZ-B09", "name": "Inadequate cleaning or disinfection", "description": "Residual contamination after reprocessing.", "category": "biological", "source_standard": "ISO 14971"},
    {"code": "HZ-B10", "name": "Biofilm formation", "description": "Biofilm on device surface leading to infection or occlusion.", "category": "biological", "source_standard": "ISO 14971"},
    {"code": "HZ-B11", "name": "Immunogenicity", "description": "Unwanted immune response to device or biologic component.", "category": "biological", "source_standard": "ISO 10993"},
    {"code": "HZ-B12", "name": "Genotoxicity or carcinogenicity", "description": "Potential for genetic damage or cancer from materials.", "category": "biological", "source_standard": "ISO 10993"},
    {"code": "HZ-B13", "name": "Hemolysis or thrombosis", "description": "Blood damage or clot formation from blood-contacting device.", "category": "biological", "source_standard": "ISO 10993"},
    {"code": "HZ-B14", "name": "Particulate or foreign body", "description": "Particulate or foreign material introduced into body.", "category": "biological", "source_standard": "ISO 14971"},
    {"code": "HZ-B15", "name": "Incorrect or contaminated biologic", "description": "Wrong or contaminated biologic (e.g. wrong blood product).", "category": "biological", "source_standard": "ISO 14971"},
    # --- CHEMICAL (15) ---
    {"code": "HZ-C01", "name": "Exposure to hazardous chemical", "description": "User or patient exposure to toxic, corrosive, or irritant chemical.", "category": "chemical", "source_standard": "ISO 14971"},
    {"code": "HZ-C02", "name": "Chemical incompatibility", "description": "Reaction between device material and drug or fluid.", "category": "chemical", "source_standard": REF},
    {"code": "HZ-C03", "name": "Residual sterilant or cleaning agent", "description": "Harmful residual from sterilization or cleaning process.", "category": "chemical", "source_standard": "ISO 14971"},
    {"code": "HZ-C04", "name": "Leachables from packaging or device", "description": "Migration of chemicals from packaging or device into product.", "category": "chemical", "source_standard": "ISO 10993, ICH Q3D"},
    {"code": "HZ-C05", "name": "Wrong or mislabeled substance", "description": "Incorrect chemical, concentration, or label leading to misuse.", "category": "chemical", "source_standard": "ISO 14971"},
    {"code": "HZ-C06", "name": "Gas or vapor release", "description": "Release of harmful or asphyxiant gas or vapor.", "category": "chemical", "source_standard": REF},
    {"code": "HZ-C07", "name": "Oxidizer or reactive hazard", "description": "Fire or reaction from oxidizer or reactive chemical.", "category": "chemical", "source_standard": REF},
    {"code": "HZ-C08", "name": "Drug degradation or instability", "description": "Degradation of drug or active substance in or by device.", "category": "chemical", "source_standard": "ISO 14971"},
    {"code": "HZ-C09", "name": "pH or osmolarity outside safe range", "description": "Delivered solution outside physiologically acceptable range.", "category": "chemical", "source_standard": REF},
    {"code": "HZ-C10", "name": "Contamination with foreign chemical", "description": "Device or fluid contaminated with unintended chemical.", "category": "chemical", "source_standard": "ISO 14971"},
    {"code": "HZ-C11", "name": "Sensitization or chronic exposure", "description": "Repeated or chronic exposure causing sensitization or toxicity.", "category": "chemical", "source_standard": "ISO 10993"},
    {"code": "HZ-C12", "name": "Incorrect concentration or dilution", "description": "Wrong concentration delivered due to software, labeling, or mixing.", "category": "chemical", "source_standard": "ISO 14971"},
    {"code": "HZ-C13", "name": "Reaction with tissue or fluid", "description": "Unintended chemical reaction with patient tissue or bodily fluid.", "category": "chemical", "source_standard": "ISO 14971"},
    {"code": "HZ-C14", "name": "Off-gassing in confined space", "description": "Build-up of volatile compounds in confined use environment.", "category": "chemical", "source_standard": REF},
    {"code": "HZ-C15", "name": "Explosive or flammable mixture", "description": "Formation of explosive or flammable mixture (e.g. with oxygen).", "category": "chemical", "source_standard": REF},
    # --- CYBERSECURITY (15) ---
    {"code": "HZ-Y01", "name": "Unauthorized access to device", "description": "Attacker gaining logical or physical access to device functions or data.", "category": "cybersecurity", "source_standard": "IEC 62443, FDA guidance"},
    {"code": "HZ-Y02", "name": "Malware or ransomware", "description": "Malicious software compromising availability or integrity of device.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y03", "name": "Data breach or exfiltration", "description": "Unauthorized disclosure of PHI or device data.", "category": "cybersecurity", "source_standard": "IEC 62443, HIPAA"},
    {"code": "HZ-Y04", "name": "Man-in-the-middle or tampering", "description": "Interception or modification of data in transit.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y05", "name": "Denial of service", "description": "Attack preventing device or network from functioning.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y06", "name": "Insecure default or weak credential", "description": "Default passwords or weak authentication allowing access.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y07", "name": "Unpatched vulnerability", "description": "Known vulnerability not patched leading to exploit.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y08", "name": "Insecure communication", "description": "Unencrypted or weakly protected communication channel.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y09", "name": "Inappropriate privilege or access control", "description": "Over-privileged user or process causing unintended changes.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y10", "name": "Supply chain compromise", "description": "Compromised component or software in supply chain.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y11", "name": "Therapeutic or safety function override", "description": "Attacker altering therapy parameters or disabling safety function.", "category": "cybersecurity", "source_standard": "FDA guidance"},
    {"code": "HZ-Y12", "name": "Insecure update mechanism", "description": "Firmware or software update without integrity or authenticity check.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y13", "name": "Insufficient audit or logging", "description": "Inability to detect or investigate security events.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y14", "name": "Physical tampering", "description": "Unauthorized physical modification of device or interface.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    {"code": "HZ-Y15", "name": "Social engineering or phishing", "description": "User tricked into revealing credentials or performing unsafe action.", "category": "cybersecurity", "source_standard": "IEC 62443"},
    # --- USABILITY (15) ---
    {"code": "HZ-U01", "name": "Use error leading to wrong setting", "description": "User selecting or confirming wrong parameter (dose, mode, patient).", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U02", "name": "Inadequate or confusing labeling", "description": "Label or instruction leading to misuse or misunderstanding.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U03", "name": "Inadvertent activation or deactivation", "description": "User accidentally turning function on or off.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U04", "name": "Inadequate feedback or visibility", "description": "User unable to perceive state, alarm, or result.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U05", "name": "Workload or stress-induced error", "description": "High workload or stress leading to use error.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U06", "name": "Incorrect interpretation of display", "description": "Misreading or misinterpreting numbers, units, or graphics.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U07", "name": "Alarm fatigue or ignoring alarm", "description": "User ignoring or disabling alarm due to excessive or nuisance alarms.", "category": "usability", "source_standard": "IEC 60601-1-8, IEC 62366-1"},
    {"code": "HZ-U08", "name": "Inadequate training or instruction", "description": "User not adequately trained or informed for safe use.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U09", "name": "Slip or mistake in sequence", "description": "Omitting step or performing steps in wrong order.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U10", "name": "Accessibility or visibility barrier", "description": "User with disability or in poor lighting unable to use safely.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U11", "name": "Confusion between similar devices or functions", "description": "User confusing device with another or confusing modes.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U12", "name": "Inadequate error recovery", "description": "User unable to correct error or recover from fault state.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U13", "name": "Reasonable foreseeable misuse", "description": "Use in a way not intended but predictable (ISO 14971).", "category": "usability", "source_standard": "ISO 14971, IEC 62366-1"},
    {"code": "HZ-U14", "name": "Inconsistent or non-intuitive control", "description": "Control layout or behavior inconsistent with user expectation.", "category": "usability", "source_standard": "IEC 62366-1"},
    {"code": "HZ-U15", "name": "Inadequate visibility of critical status", "description": "Critical status (e.g. therapy on, battery low) not sufficiently visible.", "category": "usability", "source_standard": "IEC 62366-1"},
    # --- ENVIRONMENTAL (15) ---
    {"code": "HZ-V01", "name": "Inadequate performance in specified environment", "description": "Device failing or behaving unsafely within its environmental specification.", "category": "environmental", "source_standard": "IEC 60601-1"},
    {"code": "HZ-V02", "name": "Ingress of liquid or solid", "description": "Water, dust, or foreign material entering enclosure (IP).", "category": "environmental", "source_standard": "IEC 60529, IEC 60601-1"},
    {"code": "HZ-V03", "name": "Humidity or condensation", "description": "High humidity or condensation affecting function or safety.", "category": "environmental", "source_standard": "IEC 60601-1"},
    {"code": "HZ-V04", "name": "Vibration or mechanical shock", "description": "Vibration or shock causing malfunction or damage.", "category": "environmental", "source_standard": "IEC 60601-1"},
    {"code": "HZ-V05", "name": "Altitude or pressure", "description": "Use at altitude or pressure outside specification affecting performance.", "category": "environmental", "source_standard": "IEC 60601-1"},
    {"code": "HZ-V06", "name": "Electromagnetic environment", "description": "EM field in environment causing malfunction (susceptibility).", "category": "environmental", "source_standard": "IEC 60601-1-2"},
    {"code": "HZ-V07", "name": "Lightning or surge", "description": "Lightning or power surge damaging device or causing unsafe state.", "category": "environmental", "source_standard": "IEC 60601-1"},
    {"code": "HZ-V08", "name": "Contamination from use environment", "description": "Dust, chemical, or biologic from environment contaminating device.", "category": "environmental", "source_standard": "ISO 14971"},
    {"code": "HZ-V09", "name": "Inadequate storage or transport", "description": "Damage or degradation from storage or transport conditions.", "category": "environmental", "source_standard": "ISO 14971"},
    {"code": "HZ-V10", "name": "Flood or water exposure", "description": "Exposure to flood or water beyond design (e.g. in home care).", "category": "environmental", "source_standard": "IEC 60601-1"},
    {"code": "HZ-V11", "name": "Oxygen-enriched atmosphere", "description": "Use in oxygen-enriched atmosphere increasing fire risk.", "category": "environmental", "source_standard": "IEC 60601-1"},
    {"code": "HZ-V12", "name": "Interference from other equipment", "description": "Nearby equipment affecting device function (EMI, physical).", "category": "environmental", "source_standard": "IEC 60601-1-2"},
    {"code": "HZ-V13", "name": "Loss of power or utilities", "description": "Loss of mains power or gas affecting continuous therapy.", "category": "environmental", "source_standard": "ISO 14971"},
    {"code": "HZ-V14", "name": "Inadequate disposal or environmental release", "description": "Hazard from disposal or release of device or substance.", "category": "environmental", "source_standard": "ISO 14971"},
    {"code": "HZ-V15", "name": "Combined environmental stress", "description": "Combination of environmental factors causing unexpected failure.", "category": "environmental", "source_standard": "IEC 60601-1"},
    # --- STERILITY (15) ---
    {"code": "HZ-ST01", "name": "Loss of sterility before use", "description": "Packaging breach or expiry leading to non-sterile device.", "category": "sterility", "source_standard": "ISO 11737, ISO 14971"},
    {"code": "HZ-ST02", "name": "Inadequate sterilization process", "description": "Sterilization cycle not achieving required SAL.", "category": "sterility", "source_standard": "ISO 17665, ISO 14971"},
    {"code": "HZ-ST03", "name": "Packaging failure or breach", "description": "Sterile barrier compromised before aseptic presentation.", "category": "sterility", "source_standard": "ISO 11607"},
    {"code": "HZ-ST04", "name": "Non-sterile fluid or path", "description": "Fluid path or delivered fluid not sterile.", "category": "sterility", "source_standard": "ISO 14971"},
    {"code": "HZ-ST05", "name": "Contamination during aseptic transfer", "description": "Introduction of contamination during opening or transfer.", "category": "sterility", "source_standard": "ISO 14971"},
    {"code": "HZ-ST06", "name": "Incorrect sterilization method", "description": "Device sterilized by method that damages it or fails to sterilize.", "category": "sterility", "source_standard": "ISO 17665"},
    {"code": "HZ-ST07", "name": "Residual sterilant or by-product", "description": "Harmful residual from ethylene oxide or other sterilant.", "category": "sterility", "source_standard": "ISO 10993, ISO 14971"},
    {"code": "HZ-ST08", "name": "Reuse of single-use device", "description": "Reuse of device intended for single use leading to contamination risk.", "category": "sterility", "source_standard": "ISO 14971"},
    {"code": "HZ-ST09", "name": "Inadequate reprocessing", "description": "Cleaning or sterilization of reusable device not achieving required outcome.", "category": "sterility", "source_standard": "ISO 14971"},
    {"code": "HZ-ST10", "name": "Expired sterile product", "description": "Use of device past its sterile shelf life.", "category": "sterility", "source_standard": "ISO 14971"},
    {"code": "HZ-ST11", "name": "Bioburden out of specification", "description": "Pre-sterilization bioburden too high for validated cycle.", "category": "sterility", "source_standard": "ISO 11737"},
    {"code": "HZ-ST12", "name": "Sterile barrier not maintained", "description": "Barrier integrity lost in storage or handling.", "category": "sterility", "source_standard": "ISO 11607"},
    {"code": "HZ-ST13", "name": "Wrong sterilization parameters", "description": "Cycle run with wrong time, temperature, or concentration.", "category": "sterility", "source_standard": "ISO 17665"},
    {"code": "HZ-ST14", "name": "Particulate in sterile field", "description": "Particulate introduced into sterile field or wound.", "category": "sterility", "source_standard": "ISO 14971"},
    {"code": "HZ-ST15", "name": "Inadequate aseptic technique", "description": "User technique allowing contamination during use.", "category": "sterility", "source_standard": "ISO 14971"},
]


def seed_hazard_library():
    db = SessionLocal()
    try:
        from sqlalchemy import func
        count = db.query(func.count(HazardLibrary.id)).scalar() or 0
        if count > 0:
            print(f"hazard_library already has {count} rows. Skipping seed (run with --force to replace).")
            return
        for i, h in enumerate(HAZARDS):
            rec = HazardLibrary(
                code=h["code"],
                name=h["name"],
                description=h["description"],
                category=h["category"],
                source_standard=h["source_standard"],
                is_active=True,
            )
            db.add(rec)
        db.commit()
        print(f"Seeded hazard_library with {len(HAZARDS)} hazards.")
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Run even if table already has rows (adds new only by code)")
    args = parser.parse_args()
    if args.force:
        db = SessionLocal()
        try:
            existing_codes = {r[0] for r in db.query(HazardLibrary.code).filter(HazardLibrary.code.isnot(None)).all()}
            added = 0
            for h in HAZARDS:
                if h["code"] in existing_codes:
                    continue
                rec = HazardLibrary(
                    code=h["code"],
                    name=h["name"],
                    description=h["description"],
                    category=h["category"],
                    source_standard=h["source_standard"],
                    is_active=True,
                )
                db.add(rec)
                added += 1
            db.commit()
            print(f"Added {added} new hazards (skipped {len(HAZARDS) - added} already present).")
        finally:
            db.close()
    else:
        seed_hazard_library()
