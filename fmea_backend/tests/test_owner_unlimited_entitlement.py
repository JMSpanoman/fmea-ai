"""Owner grant, identity rebinding, and unchanged customer limits."""
from datetime import datetime, timedelta, timezone
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth.entitlements import (
    DEV_OWNER_AUTH0_ID,
    OWNER_UNLIMITED_LABEL,
    OWNER_VERIFIED_EMAIL,
    SR1_API_AUDIENCE,
    VerifiedIdentity,
    attach_entitlement,
    evaluate_entitlement,
    production_auth0_configuration_error,
    user_has_permanent_unlimited,
)
from auth.plan import enforce_trial_project_limit, get_user_plan
from auth.security import verify_auth0_token
from business_logic.owner_identity_migration import (
    apply_owner_identity_migration,
    rollback_owner_identity_migration,
)
from business_logic.team_access import MAX_TEAM_SEATS
from crud import project as projects
from database import Base
from models.account_entitlement import AccountEntitlement, IdentityMigration
from models.component import Component
from models.fmea import FMEARow
from models.project import Project
from models.user import User
from schemas.project import ProjectCreate


ISSUER = "https://tenant.example.auth0.com/"
SUBJECT = "auth0|john-real"


@pytest.fixture
def db(monkeypatch):
    monkeypatch.setenv("AUTH0_DOMAIN", "tenant.example.auth0.com")
    monkeypatch.setenv("SMARTRISK_DEV_FORCE_PRO", "false")
    monkeypatch.setenv("ENVIRONMENT", "test")
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield session


def owner_identity(**overrides):
    data = dict(issuer=ISSUER, subject=SUBJECT, email=OWNER_VERIFIED_EMAIL, email_verified=True, algorithm="RS256")
    data.update(overrides)
    return VerifiedIdentity(**data)


def add_user(db, **kwargs):
    user = User(id=kwargs.pop("id", str(uuid.uuid4())), email=kwargs.pop("email"), plan=kwargs.pop("plan", "lite"), **kwargs)
    db.add(user)
    db.commit()
    return user


def test_existing_customer_limits_are_unchanged(db):
    assert MAX_TEAM_SEATS == 5
    trial = add_user(db, id="trial", auth0_id="auth0|trial", email="trial@example.com", plan="lite",
                     trial_ends_at=datetime.now(timezone.utc) + timedelta(days=2))
    projects.create_project(db, ProjectCreate(name="Only"), trial.id)
    with pytest.raises(HTTPException) as blocked:
        projects.create_project(db, ProjectCreate(name="Second"), trial.id)
    assert blocked.value.status_code == 403
    enforce_trial_project_limit(trial, 0)
    with pytest.raises(HTTPException):
        enforce_trial_project_limit(trial, 1)

    paid = add_user(db, id="paid", auth0_id="auth0|paid", email="paid@example.com", plan="pro", subscription_status="active")
    for name in ("One", "Two", "Three"):
        projects.create_project(db, ProjectCreate(name=name), paid.id)
    with pytest.raises(HTTPException) as fourth:
        projects.create_project(db, ProjectCreate(name="Four"), paid.id)
    assert fourth.value.status_code == 403
    assert "three projects" in fourth.value.detail

    legacy = add_user(db, id="legacy", auth0_id="auth0|legacy", email="legacy@example.com", plan="pro")
    for index in range(4):
        projects.create_project(db, ProjectCreate(name=f"Legacy {index}"), legacy.id)
    assert db.query(Project).filter_by(user_id="legacy").count() == 4


def test_verified_owner_keeps_access_and_can_pass_the_team_project_cap(db):
    john = add_user(
        db, id="john-id", auth0_id=SUBJECT, email=OWNER_VERIFIED_EMAIL, plan="lite",
        subscription_status="canceled", trial_ends_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    decision = attach_entitlement(john, evaluate_entitlement(db, john, owner_identity()))
    assert decision.unlimited is True
    assert decision.permanent is True
    assert decision.label == OWNER_UNLIMITED_LABEL
    assert decision.as_api()["quotas"] == {
        "projects": None, "components": None, "fmea_analyses": None,
        "ai_generations": None, "reports": None, "exports": None,
    }
    assert get_user_plan(john) == "pro"
    john.plan = "lite"
    john.subscription_status = "canceled"
    db.commit()
    assert user_has_permanent_unlimited(db, john) is True
    assert db.query(AccountEntitlement).count() == 1
    for index in range(4):
        projects.create_project(db, ProjectCreate(name=f"Owner {index}"), john.id)
    assert db.query(Project).filter_by(user_id="john-id").count() == 4


def test_typed_email_profile_and_dev_token_do_not_receive_the_grant(db):
    impostor = add_user(db, auth0_id="auth0|impostor", email="impostor@example.com", plan="lite")
    impostor.email = OWNER_VERIFIED_EMAIL
    db.commit()
    refused = evaluate_entitlement(db, impostor, owner_identity(email="impostor@example.com"))
    assert refused.unlimited is False
    assert db.query(AccountEntitlement).count() == 0

    dev = add_user(db, auth0_id=DEV_OWNER_AUTH0_ID, email=OWNER_VERIFIED_EMAIL, plan="pro")
    dev_decision = evaluate_entitlement(
        db, dev, VerifiedIdentity(None, DEV_OWNER_AUTH0_ID, OWNER_VERIFIED_EMAIL, True, "HS256")
    )
    assert dev_decision.unlimited is False
    unverified = evaluate_entitlement(db, dev, owner_identity(email_verified=False))
    assert unverified.unlimited is False
    assert db.query(AccountEntitlement).count() == 0


def test_identity_migration_preserves_ownership_and_rolls_back(db):
    john = add_user(db, id="owner-row", auth0_id=DEV_OWNER_AUTH0_ID, email=OWNER_VERIFIED_EMAIL, plan="pro")
    same_email = add_user(db, id="other-row", auth0_id="auth0|someone-else", email=OWNER_VERIFIED_EMAIL, plan="lite")
    project = projects.create_project(db, ProjectCreate(name="Existing"), john.id)
    component = Component(id="component-1", project_id=project.id, name="Lead")
    row = FMEARow(id="fmea-1", project_id=project.id, failure_mode="Fracture")
    db.add_all([component, row])
    db.commit()

    result = apply_owner_identity_migration(db, owner_identity())
    assert result.status == "applied"
    assert result.user_id == "owner-row"
    db.refresh(john)
    db.refresh(same_email)
    db.refresh(project)
    assert john.auth0_id == SUBJECT
    assert john.id == "owner-row"
    assert same_email.auth0_id == "auth0|someone-else"
    assert same_email.id == "other-row"
    assert project.user_id == "owner-row"
    assert db.get(Component, "component-1").project_id == project.id
    assert db.get(FMEARow, "fmea-1").project_id == project.id
    assert projects.get_project(db, project.id, john.id).id == project.id
    assert projects.get_project(db, project.id, same_email.id) is None

    again = apply_owner_identity_migration(db, owner_identity())
    assert again.status == "already_applied"
    assert db.query(IdentityMigration).filter_by(status="applied").count() == 1

    rolled = rollback_owner_identity_migration(db, john.id)
    assert rolled.status == "rolled_back"
    db.refresh(john)
    db.refresh(project)
    assert john.auth0_id == DEV_OWNER_AUTH0_ID
    assert project.user_id == "owner-row"
    assert db.get(FMEARow, "fmea-1").id == "fmea-1"


def test_migration_does_not_merge_a_different_account_that_already_has_the_subject(db):
    dev = add_user(db, id="dev-row", auth0_id=DEV_OWNER_AUTH0_ID, email=OWNER_VERIFIED_EMAIL, plan="pro")
    existing = add_user(db, id="auth0-row", auth0_id=SUBJECT, email="other@example.com", plan="lite")
    project = projects.create_project(db, ProjectCreate(name="Dev work"), dev.id)
    result = apply_owner_identity_migration(db, owner_identity())
    assert result.status == "conflict"
    db.refresh(dev)
    db.refresh(existing)
    db.refresh(project)
    assert dev.auth0_id == DEV_OWNER_AUTH0_ID
    assert existing.auth0_id == SUBJECT
    assert project.user_id == "dev-row"
    assert db.query(IdentityMigration).filter_by(status="conflict").count() == 1


def test_production_requires_explicit_auth0_configuration(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("AUTH0_DOMAIN", raising=False)
    monkeypatch.delenv("API_AUDIENCE", raising=False)
    monkeypatch.delenv("AUTH0_AUDIENCE", raising=False)
    assert production_auth0_configuration_error() == "AUTH0_DOMAIN is not set"
    monkeypatch.setenv("AUTH0_DOMAIN", "tenant.example.auth0.com")
    monkeypatch.setenv("API_AUDIENCE", "https://wrong.example/api")
    assert "API_AUDIENCE" in production_auth0_configuration_error()
    monkeypatch.setenv("API_AUDIENCE", SR1_API_AUDIENCE)
    assert production_auth0_configuration_error() is None
    assert verify_auth0_token("not-a-token") is None
