"""
Ensure the public-demo user and dashboard project exist.

Idempotent. Does not print DATABASE_URL, tokens, or credentials.

Controlled by:
  DEMO_ENSURE_PROJECT=true          required to run (also the process entry gate)
  DEMO_PROJECT_ID                   default: cd214464-e10b-488a-86dc-f24022508b60
  DEMO_USER_EMAIL                   default: gridmatrix@gridmatrix.com
  DEMO_REASSIGN_PROJECT=true        if the project already exists, move ownership
                                    to the demo user (production demo only)
"""
from __future__ import annotations

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crud import user as user_crud
from models.project import Project
from models.user import PLAN_PRO

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("ensure_demo_project")

DEFAULT_PROJECT_ID = "cd214464-e10b-488a-86dc-f24022508b60"
DEFAULT_EMAIL = "gridmatrix@gridmatrix.com"
DEFAULT_NAME = "Implantable Pacemaker: Test"
DEFAULT_DESCRIPTION = "Demonstration project for SmartRisk 1 public demo."


def _flag(name: str, default: str = "") -> bool:
    return str(os.getenv(name, default) or "").strip().lower() in {"1", "true", "yes", "on"}


def ensure_demo_project() -> None:
    if not _flag("DEMO_ENSURE_PROJECT"):
        logger.debug("DEMO_ENSURE_PROJECT is not enabled; skipping")
        return

    import models  # noqa: F401 — register SQLAlchemy tables
    from database import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)

    project_id = (os.getenv("DEMO_PROJECT_ID") or DEFAULT_PROJECT_ID).strip()
    email = (os.getenv("DEMO_USER_EMAIL") or DEFAULT_EMAIL).strip().lower()
    reassign = _flag("DEMO_REASSIGN_PROJECT")
    if not project_id or not email:
        raise SystemExit("DEMO_PROJECT_ID and DEMO_USER_EMAIL must be non-empty")

    auth0_id = f"dev:{email}"
    db = SessionLocal()
    try:
        user = user_crud.get_user_by_auth0_id(db, auth0_id) or user_crud.get_user_by_email(db, email)
        if not user:
            user = user_crud.create_user_from_auth0(db, auth0_id, email)
        if not user:
            raise SystemExit("Failed to create demo user")

        if getattr(user, "plan", None) != PLAN_PRO:
            user.plan = PLAN_PRO
            db.add(user)
            db.commit()
            db.refresh(user)

        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            if project.user_id != user.id:
                if not reassign:
                    logger.info(
                        "Demo project %s exists under another owner; leaving ownership unchanged",
                        project_id,
                    )
                else:
                    project.user_id = user.id
                    db.add(project)
                    db.commit()
                    logger.info("Reassigned demo project %s to demo user", project_id)
            else:
                logger.info("Demo project %s already owned by demo user", project_id)
            return

        project = Project(
            id=project_id,
            user_id=user.id,
            name=DEFAULT_NAME,
            description=DEFAULT_DESCRIPTION,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        from business_logic.project_initializer import initialize_project_required_docs

        created = initialize_project_required_docs(db, project.id)
        logger.info("Created demo project %s with %s starter documents", project_id, len(created))
    finally:
        db.close()


if __name__ == "__main__":
    ensure_demo_project()
