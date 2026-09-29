from datetime import timedelta
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User
from business_logic import team_access as teams
from crud import project as projects
from schemas.project import ProjectCreate
from auth.plan import get_user_plan


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield session


def make_user(db, name, paid=False):
    user = User(id=name, auth0_id=f"auth0|{name}", email=f"{name}@example.com",
                plan="pro" if paid else "lite", subscription_status="active" if paid else None)
    db.add(user); db.commit()
    user.is_verified = True
    return user


def test_pending_invitations_reserve_seats_and_expired_ones_release_them(db):
    owner = make_user(db, "owner", True)
    for i in range(4): teams.invite(db, owner, f"member{i}@example.com")
    with pytest.raises(HTTPException) as error: teams.invite(db, owner, "sixth@example.com")
    assert error.value.status_code == 409
    db.rollback()
    first = teams.pending_invitations(db, owner.id).first()
    first.expires_at = teams.utcnow() - timedelta(seconds=1); db.commit()
    teams.invite(db, owner, "sixth@example.com")
    assert teams.pending_invitations(db, owner.id).count() == 4


def test_invitation_binds_verified_email_and_cannot_be_replayed(db):
    owner = make_user(db, "owner", True)
    member = make_user(db, "member")
    stranger = make_user(db, "stranger")
    invitation, token = teams.invite(db, owner, member.email)
    with pytest.raises(HTTPException): teams.accept(db, stranger, token)
    db.rollback()
    assert stranger.team_owner_id is None
    member.is_verified = False
    with pytest.raises(HTTPException): teams.accept(db, member, token)
    member.is_verified = True
    teams.accept(db, member, token)
    assert member.team_owner_id == owner.id
    with pytest.raises(HTTPException) as error: teams.accept(db, member, token)
    assert error.value.status_code == 410


def test_shared_projects_isolate_teams_enforce_quota_and_revoke_access(db):
    owner = make_user(db, "owner", True)
    member = make_user(db, "member")
    outsider = make_user(db, "outsider", True)
    _, token = teams.invite(db, owner, member.email)
    teams.accept(db, member, token)
    project = projects.create_project(db, ProjectCreate(name="Shared FMEA"), member.id)
    assert project.user_id == owner.id
    assert projects.get_project(db, project.id, member.id) is not None
    assert projects.get_project(db, project.id, outsider.id) is None
    projects.create_project(db, ProjectCreate(name="Second"), owner.id)
    projects.create_project(db, ProjectCreate(name="Third"), member.id)
    with pytest.raises(HTTPException) as error:
        projects.create_project(db, ProjectCreate(name="Fourth"), member.id)
    assert error.value.status_code == 403
    member.billing_owner = owner
    assert get_user_plan(member) == "pro"
    owner.subscription_status = "canceled"; owner.plan = "lite"; db.commit()
    assert get_user_plan(member) == "lite"
    teams.remove_member(db, owner, member.id)
    assert projects.get_project(db, project.id, member.id) is None
    assert projects.get_project(db, project.id, owner.id) is not None
