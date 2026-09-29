"""A saved, editable example using the same project quota as a blank project."""
from crud.project import create_project
from models.fmea import FMEARow
from schemas.project import ProjectCreate


def create_sample_project(db, user_id):
    project = create_project(db, ProjectCreate(name="Sample FMEA — lab equipment",
        description="Fictional training example. Replace the example data with your own analysis. Not reviewed or approved for release."), user_id, commit=False)
    examples = [
        ("Display status", "Status indicator remains off", "Operator cannot see equipment state", "Loose connector", 3, 2, 2, "Check connection and verify indicator during startup"),
        ("Store settings", "Settings are not saved", "Operator repeats setup", "Interrupted save", 2, 3, 2, "Confirm saved settings and test recovery after interruption"),
    ]
    for function, failure, effect, cause, severity, probability, detection, mitigation in examples:
        db.add(FMEARow(project_id=project.id, device_function=function, failure_mode=failure,
            effect=effect, cause=cause, severity=severity, probability=probability, detection=detection,
            rpn=severity * probability * detection, mitigation=mitigation,
            acceptable_for_release=False, approval_blocked=True,
            ai_metadata={"sample": True, "review_required": True}))
    db.commit()
    db.refresh(project)
    return project
