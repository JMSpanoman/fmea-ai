"""Exercise customer access through the real HTTP routes in an isolated database.

Identity is supplied locally; this does not replace deployed Auth0 acceptance.
"""
import os
from pathlib import Path
import subprocess
import sys


def test_team_and_trial_http_access_journey(tmp_path):
    backend = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "PYTHONPATH": str(backend),
        "DATABASE_URL": f"sqlite:///{tmp_path / 'access.db'}",
        "ENVIRONMENT": "staging",
        "ENABLE_SELF_SERVICE_TRIALS": "true",
        "ALLOW_DEV_LOGIN": "false",
        "DEMO_ENSURE_PROJECT": "false",
        "ENABLE_SR1_BILLING": "true",
        "ENABLE_LIVE_BILLING": "false",
    }
    result = subprocess.run(
        [sys.executable, "-c", '''
from datetime import datetime, timedelta, timezone
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app
from database import get_db, SessionLocal
from auth.dependencies import get_current_user
from models.user import User
from unittest.mock import patch

identity = {"id": "owner"}
def current_identity(db: Session = Depends(get_db)):
    user = db.get(User, identity["id"])
    user.is_verified = True
    user.billing_owner = db.get(User, user.team_owner_id) if user.team_owner_id else user
    return user

app.dependency_overrides[get_current_user] = current_identity
with TestClient(app) as client:
    with SessionLocal() as db:
        for name in ("owner", "member", "outsider", "trial"):
            db.add(User(id=name, auth0_id=f"auth0|{name}", email=f"{name}@example.com",
                        plan="pro" if name == "owner" else "lite",
                        subscription_status="active" if name == "owner" else None,
                        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=14)))
        db.commit()

    response = client.post("/projects/sample")
    assert response.status_code == 201, response.text
    project_id = response.json()["id"]
    response = client.post("/team/invitations", json={"email": "member@example.com"})
    assert response.status_code == 201, response.text
    token = response.json()["token"]
    identity["id"] = "outsider"
    assert client.post("/team/accept", json={"token": token}).status_code == 403
    assert client.get(f"/projects/{project_id}").status_code == 404
    identity["id"] = "member"
    assert client.post("/team/accept", json={"token": token}).status_code == 200
    assert client.post("/team/accept", json={"token": token}).status_code == 410
    assert client.get("/team").json()["is_owner"] is False
    assert client.get(f"/projects/{project_id}").status_code == 200
    assert client.get(f"/projects/{project_id}/documents").status_code == 200
    assert client.put(f"/projects/{project_id}", json={"description": "Retained member edit"}).status_code == 200
    assert client.post("/team/invitations", json={"email": "forbidden@example.com"}).status_code == 403
    # The member must be rejected before any Stripe operation is attempted.
    with patch("routers.billing._configured", return_value=(None, None)):
        assert client.post("/billing/checkout", json={"interval": "monthly"}).status_code == 403
    for name in ("Shared second", "Shared third"):
        response = client.post("/projects", json={"name": name})
        assert response.status_code == 201, response.text
    assert client.post("/projects", json={"name": "Over shared quota"}).status_code == 403

    identity["id"] = "owner"
    assert len(client.get("/projects").json()) == 3
    assert client.get(f"/projects/{project_id}").json()["description"] == "Retained member edit"
    invitation_ids = []
    for i in range(3):
        response = client.post("/team/invitations", json={"email": f"pending{i}@example.com"})
        assert response.status_code == 201, response.text
        invitation_ids.append(response.json()["id"])
    assert client.post("/team/invitations", json={"email": "sixth@example.com"}).status_code == 409
    assert client.delete(f"/team/invitations/{invitation_ids[0]}").status_code == 204
    assert client.post("/team/invitations", json={"email": "replacement@example.com"}).status_code == 201

    with SessionLocal() as db:
        owner = db.get(User, "owner")
        owner.subscription_status = "past_due"
        db.commit()
    identity["id"] = "member"
    assert client.get(f"/projects/{project_id}").status_code == 403
    assert client.get("/billing/status").status_code == 200
    with SessionLocal() as db:
        db.get(User, "owner").subscription_status = "active"
        db.commit()
    assert client.get(f"/projects/{project_id}").status_code == 200
    identity["id"] = "owner"
    assert client.delete("/team/members/member").status_code == 204
    identity["id"] = "member"
    assert client.get(f"/projects/{project_id}").status_code == 404
    assert client.get(f"/projects/{project_id}/documents").status_code == 404
    identity["id"] = "owner"
    assert client.get(f"/projects/{project_id}").json()["description"] == "Retained member edit"

    identity["id"] = "trial"
    assert client.post("/projects/sample").status_code == 201
    assert client.post("/projects", json={"name": "Second trial project"}).status_code == 403
    with SessionLocal() as db:
        db.get(User, "trial").trial_ends_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    assert client.get("/projects").status_code == 403
    assert client.get("/billing/status").status_code == 200
app.dependency_overrides.clear()
'''],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
