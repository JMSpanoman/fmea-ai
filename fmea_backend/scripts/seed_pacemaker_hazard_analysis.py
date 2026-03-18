"""
Seed hazard analysis items for an implantable pacemaker example.
Creates realistic ISO 14971-style rows for: Battery, Lead, Pulse Generator, Firmware, Telemetry Module, Housing.
Run from backend root: python scripts/seed_pacemaker_hazard_analysis.py [project_id]
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.project import Project
from models.user import User
from models.component import Component
from models.hazard_analysis_item import HazardAnalysisItem
from models.project_profile import ProjectProfile
import uuid


# At least 3 hazard records per component; specific, medically plausible content (no "N/A" or generic placeholders).
SEED_HAZARDS = [
    # Battery
    {"component_name": "Battery", "hazard_category": "Electrical", "hazard": "Premature battery depletion", "foreseeable_sequence_of_events": "High impedance or elevated pacing burden causes current draw to exceed design limits; battery voltage falls below EOL indicator threshold before next scheduled follow-up.", "hazardous_situation": "Patient relies on device for pacing while battery is depleted; device may cease pacing without adequate warning.", "harm": "Loss of pacing leading to bradycardia, syncope, or cardiac arrest in pacemaker-dependent patients.", "failure_mode": "End-of-life reached earlier than labeled", "cause_of_failure": "Higher-than-expected current drain (e.g. high capture thresholds, lead issues).", "initial_severity": 9, "initial_probability": 2, "initial_risk_level": "High", "risk_control_measures": ["EOL indicator and elective replacement indicator in software", "Patient and physician labeling for follow-up schedule", "Remote monitoring to trend battery voltage"], "residual_severity": 5, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Battery", "hazard_category": "Chemical", "hazard": "Battery leakage or thermal runaway", "foreseeable_sequence_of_events": "Defective seal or internal short causes electrolyte leakage or overheating; chemicals or heat damage surrounding tissue or electronics.", "hazardous_situation": "Patient has implanted device with leaking or overheating battery in body.", "harm": "Tissue damage, inflammation, or systemic toxicity; potential need for explant.", "failure_mode": "Battery seal failure or internal short", "cause_of_failure": "Manufacturing defect, mechanical damage, or end-of-life degradation.", "initial_severity": 8, "initial_probability": 1, "initial_risk_level": "Medium", "risk_control_measures": ["Qualification testing per ISO 13485", "Hermetic seal verification", "Design margins for thermal and mechanical stress"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Battery", "hazard_category": "Electrical", "hazard": "Intermittent power loss during high demand", "foreseeable_sequence_of_events": "Transient high current (e.g. defibrillation protection, MRI) causes voltage dip; device may reset or suspend therapy briefly.", "hazardous_situation": "Patient receives external defibrillation or is in MRI; device experiences brownout.", "harm": "Temporary loss of pacing; syncope or injury if pacing-dependent.", "failure_mode": "Voltage brownout under peak load", "cause_of_failure": "Battery internal resistance under pulse load.", "initial_severity": 7, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["Capacitor support for pulse loads", "Testing per IEC 60601-2-52", "Labeling for MRI and defibrillation"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    # Lead
    {"component_name": "Lead", "hazard_category": "Mechanical", "hazard": "Lead fracture or conductor failure", "foreseeable_sequence_of_events": "Flex fatigue at stress points (e.g. clavicle, tricuspid) or manufacturing defect leads to conductor fracture; pacing/sensing lost or intermittent.", "hazardous_situation": "Patient has fractured lead; device may oversense, undersense, or fail to pace.", "harm": "Inappropriate therapy (e.g. withheld pacing), syncope, or need for lead revision.", "failure_mode": "Conductor fracture or insulation breach", "cause_of_failure": "Mechanical stress, design margin, or manufacturing defect.", "initial_severity": 8, "initial_probability": 3, "initial_risk_level": "High", "risk_control_measures": ["Lead design and fatigue testing", "Implant technique training", "Remote monitoring for lead integrity"], "residual_severity": 5, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Lead", "hazard_category": "Biological", "hazard": "Perforation or cardiac injury at implant", "foreseeable_sequence_of_events": "Stylet or lead advancement causes atrial or ventricular perforation; pericardial effusion or tamponade may occur.", "hazardous_situation": "Clinician advances lead during implant; tip perforates myocardium.", "harm": "Pericardial effusion, tamponade, or death if unrecognized.", "failure_mode": "Tissue perforation by lead", "cause_of_failure": "Excessive force, thin wall, or sharp tip.", "initial_severity": 9, "initial_probability": 2, "initial_risk_level": "High", "risk_control_measures": ["IFU and training on technique", "Tip design and testing", "Fluoroscopy and post-implant assessment"], "residual_severity": 5, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Lead", "hazard_category": "Electrical", "hazard": "Dislodgement leading to loss of capture", "foreseeable_sequence_of_events": "Lead moves from implant position; threshold rises or loss of capture occurs; device may continue to pace without capture.", "hazardous_situation": "Patient is pacemaker-dependent; lead has dislodged and pacing is ineffective.", "harm": "Bradycardia, syncope, or cardiac arrest.", "failure_mode": "Lead dislodgement", "cause_of_failure": "Insufficient fixation, patient activity, or anatomy.", "initial_severity": 8, "initial_probability": 3, "initial_risk_level": "High", "risk_control_measures": ["Active fixation design", "Post-implant threshold check", "Follow-up and remote monitoring"], "residual_severity": 5, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    # Pulse Generator
    {"component_name": "Pulse Generator", "hazard_category": "Electrical", "hazard": "Inappropriate pacing (too fast or unnecessary)", "foreseeable_sequence_of_events": "Algorithm or sensor error (e.g. EMI, oversensing) triggers pacing at upper rate or in non-indicated situation; patient experiences palpitations or tachycardia.", "hazardous_situation": "Device delivers pacing that is not clinically indicated or at excessive rate.", "harm": "Palpitations, angina, or heart failure exacerbation in susceptible patients.", "failure_mode": "Inappropriate pacing output", "cause_of_failure": "Oversensing, algorithm bug, or EMI.", "initial_severity": 6, "initial_probability": 3, "initial_risk_level": "Medium", "risk_control_measures": ["Sensing and algorithm V&V", "EMI testing", "Programmable parameters and diagnostics"], "residual_severity": 3, "residual_probability": 2, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Pulse Generator", "hazard_category": "Software", "hazard": "Failure to deliver therapy when required", "foreseeable_sequence_of_events": "Software fault or corrupted state prevents pacing or shock delivery when brady or tachy episode occurs.", "hazardous_situation": "Patient has life-threatening arrhythmia; device does not pace or defibrillate.", "harm": "Syncope, cardiac arrest, or death.", "failure_mode": "Therapy not delivered", "cause_of_failure": "Software defect, memory corruption, or watchdog timeout.", "initial_severity": 10, "initial_probability": 1, "initial_risk_level": "Critical", "risk_control_measures": ["IEC 62304 lifecycle", "Defensive programming and watchdogs", "Integration and system testing"], "residual_severity": 5, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Pulse Generator", "hazard_category": "Mechanical", "hazard": "Hermeticity loss and moisture ingress", "foreseeable_sequence_of_events": "Crack or seal defect in housing allows body fluid ingress; corrosion or short circuit disables device.", "hazardous_situation": "Device is implanted with compromised seal; failure can occur unpredictably.", "harm": "Sudden loss of pacing or sensing; possible death in dependent patients.", "failure_mode": "Loss of hermetic seal", "cause_of_failure": "Manufacturing defect, mechanical damage, or material degradation.", "initial_severity": 9, "initial_probability": 1, "initial_risk_level": "High", "risk_control_measures": ["Hermeticity testing per ISO 13485", "Design for mechanical robustness", "Screening and lot release"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    # Firmware
    {"component_name": "Firmware", "hazard_category": "Software", "hazard": "Incorrect therapy parameter applied after update", "foreseeable_sequence_of_events": "Firmware update or programming error sets output or timing outside safe range; next therapy delivery uses wrong parameters.", "hazardous_situation": "Clinician or patient uses programmer; device accepts and applies invalid or unsafe values.", "harm": "Overstimulation, under-pacing, or pro-arrhythmia.", "failure_mode": "Invalid parameter stored or applied", "cause_of_failure": "Missing range check, UI bug, or communication error.", "initial_severity": 8, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["Parameter range checks in firmware", "Programmer and device V&V", "User training and IFU"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Firmware", "hazard_category": "Software", "hazard": "Race condition or deadlock in real-time loop", "foreseeable_sequence_of_events": "Under rare timing, scheduler or interrupt handling fails; device hangs or misses therapy delivery window.", "hazardous_situation": "Device is in state where next beat requires pacing; firmware does not respond in time.", "harm": "Dropped beat or sustained bradycardia; syncope or arrest in dependent patients.", "failure_mode": "Firmware hang or missed deadline", "cause_of_failure": "Concurrency defect or insufficient margin in timing analysis.", "initial_severity": 9, "initial_probability": 1, "initial_risk_level": "High", "risk_control_measures": ["Static and dynamic timing analysis", "Defensive watchdogs", "Stress and long-duration testing"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Firmware", "hazard_category": "Software", "hazard": "Corrupted memory or wrong mode after power event", "foreseeable_sequence_of_events": "Brownout or ESD causes non-volatile memory corruption or mode register error; device boots in wrong mode or with wrong configuration.", "hazardous_situation": "Patient has device that has experienced power glitch; therapy may be disabled or inappropriate.", "harm": "Loss of pacing or inappropriate therapy until next interrogation.", "failure_mode": "Corrupted state after power event", "cause_of_failure": "Insufficient power supervision or memory protection.", "initial_severity": 8, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["Power-on reset and memory checks", "Safe default mode", "IEC 60601 EMC and ESD testing"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    # Telemetry Module
    {"component_name": "Telemetry Module", "hazard_category": "Electrical", "hazard": "EMI from telemetry affecting therapy", "foreseeable_sequence_of_events": "During telemetry session, RF or conducted noise is sensed as cardiac signal; device withholds pacing or delivers inappropriate therapy.", "hazardous_situation": "Patient is being interrogated or monitored remotely; device misinterprets noise.", "harm": "Withheld pacing or inappropriate shock; syncope or injury.", "failure_mode": "Oversensing during telemetry", "cause_of_failure": "Inadequate filtering or blanking during RF activity.", "initial_severity": 7, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["Filtering and blanking during telemetry", "EMI testing per IEC 60601-1-2", "IFU for in-clinic and remote use"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Telemetry Module", "hazard_category": "Use Error", "hazard": "Wrong patient or device programmed via remote", "foreseeable_sequence_of_events": "Clinician selects wrong patient or device in remote platform; programming commands are sent to incorrect implant.", "hazardous_situation": "Two or more patients are in same clinic or list; one receives programming intended for another.", "harm": "Inappropriate parameters (e.g. mode, rate) leading to symptoms or loss of therapy.", "failure_mode": "Incorrect device targeted", "cause_of_failure": "UI or workflow allows selection error.", "initial_severity": 8, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["Device and patient identification checks", "User training and workflow design", "Audit trail and confirmations"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Telemetry Module", "hazard_category": "Software", "hazard": "Data breach or unauthorized access", "foreseeable_sequence_of_events": "Vulnerability in telemetry stack or cloud allows attacker to read or modify patient/device data or send commands.", "hazardous_situation": "Device or backend is connected to network; attacker gains access.", "harm": "Privacy harm; in worst case, malicious programming could affect therapy.", "failure_mode": "Unauthorized access to device or data", "cause_of_failure": "Missing authentication, weak crypto, or vulnerability in dependency.", "initial_severity": 6, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["Authentication and encryption", "Security risk analysis and penetration testing", "Secure development lifecycle"], "residual_severity": 3, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    # Housing
    {"component_name": "Housing", "hazard_category": "Mechanical", "hazard": "Sharp edge or corrosion causing tissue injury", "foreseeable_sequence_of_events": "Edge, burr, or corrosion on can causes chronic irritation, erosion, or infection at implant site.", "hazardous_situation": "Patient has device with mechanical or corrosion defect in pocket.", "harm": "Pain, erosion, infection, or need for revision.", "failure_mode": "Surface defect or biocompatibility issue", "cause_of_failure": "Manufacturing or material selection.", "initial_severity": 5, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["Biocompatibility per ISO 10993", "Surface finish and inspection", "Post-market surveillance"], "residual_severity": 3, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Housing", "hazard_category": "Mechanical", "hazard": "Device migration or flip", "foreseeable_sequence_of_events": "Pocket is too large or suture fails; device migrates or flips; lead may be dislodged or patient may feel discomfort.", "hazardous_situation": "Patient has unstable implant; lead or can moves.", "harm": "Lead dislodgement, Twiddler's syndrome, or need for revision.", "failure_mode": "Migration or rotation of can", "cause_of_failure": "Surgical technique or patient anatomy.", "initial_severity": 6, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["IFU for pocket size and fixation", "Surgeon training", "Device design for stability"], "residual_severity": 3, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
    {"component_name": "Housing", "hazard_category": "Electrical", "hazard": "EMI or ESD entering via connector or seam", "foreseeable_sequence_of_events": "EMI or ESD couples into device via header or seam; internal circuit upset or damage.", "hazardous_situation": "Patient is in high-field environment or touches connector during handling.", "harm": "Temporary malfunction or permanent damage; loss of therapy.", "failure_mode": "EMI/ESD entry", "cause_of_failure": "Insufficient shielding or filtering at connector.", "initial_severity": 7, "initial_probability": 2, "initial_risk_level": "Medium", "risk_control_measures": ["IEC 60601-1-2 EMC testing", "Connector design and labeling", "ESD controls in manufacturing"], "residual_severity": 4, "residual_probability": 1, "residual_risk_level": "Low", "residual_risk_acceptability": "acceptable"},
]


def ensure_project_and_components(db, project_id_arg: str = None):
    if project_id_arg:
        project = db.query(Project).filter(Project.id == project_id_arg).first()
        if not project:
            raise SystemExit(f"Project {project_id_arg} not found.")
        project_id = project.id
        user_id = project.user_id
    else:
        user = db.query(User).limit(1).first()
        if not user:
            raise SystemExit("No user found. Create a user first.")
        user_id = user.id
        project = db.query(Project).filter(Project.user_id == user_id).first()
        if not project:
            project = Project(
                id=str(uuid.uuid4()),
                name="Pacemaker Example",
                description="Implantable pacemaker hazard analysis example",
                user_id=user_id,
            )
            db.add(project)
            db.flush()
        project_id = project.id
    comp_names = list({h["component_name"] for h in SEED_HAZARDS})
    component_ids = {}
    for name in comp_names:
        comp = db.query(Component).filter(Component.project_id == project_id, Component.name == name).first()
        if not comp:
            comp = Component(
                id=str(uuid.uuid4()),
                project_id=project_id,
                name=name,
                description=f"Pacemaker component: {name}",
            )
            db.add(comp)
            db.flush()
        component_ids[name] = comp.id
    return project_id, user_id, component_ids


def main():
    project_id_arg = sys.argv[1] if len(sys.argv) > 1 else None
    db = SessionLocal()
    try:
        project_id, user_id, component_ids = ensure_project_and_components(db, project_id_arg or None)
        created = 0
        for i, h in enumerate(SEED_HAZARDS):
            comp_id = component_ids.get(h["component_name"])
            item = HazardAnalysisItem(
                id=str(uuid.uuid4()),
                project_id=project_id,
                component_id=comp_id,
                risk_key=f"HA-{i+1:03d}",
                version_no=1,
                hazard_category=h["hazard_category"],
                hazard=h["hazard"],
                foreseeable_sequence_of_events=h["foreseeable_sequence_of_events"],
                hazardous_situation=h["hazardous_situation"],
                harm=h["harm"],
                affected_user="Patient",
                failure_mode=h["failure_mode"],
                cause_of_failure=h["cause_of_failure"],
                clinical_effect=h.get("harm"),
                operating_mode="Normal operation",
                use_environment="Implanted; clinical and home use",
                initial_severity=h["initial_severity"],
                initial_probability=h["initial_probability"],
                initial_risk_level=h["initial_risk_level"],
                risk_control_measures=h["risk_control_measures"],
                risk_control_type=["inherent_safety_by_design", "protective_measures", "information_for_safety"],
                residual_severity=h["residual_severity"],
                residual_probability=h["residual_probability"],
                residual_risk_level=h["residual_risk_level"],
                residual_risk_acceptability=h["residual_risk_acceptability"],
                approval_status="draft",
                ai_generated=False,
                source_context="seed_pacemaker",
            )
            db.add(item)
            created += 1
        db.commit()
        print(f"Created {created} hazard analysis items for project {project_id}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
