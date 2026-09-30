"""Exercise the full app import and startup with a separate persistent SQLite DB."""
import os
from pathlib import Path
import subprocess
import sys


def test_customer_startup_schema_restart_and_migration_failure(tmp_path):
    backend = Path(__file__).resolve().parents[1]
    env = {
        **os.environ,
        "PYTHONPATH": str(backend),
        "DATABASE_URL": f"sqlite:///{tmp_path / 'fmea.db'}",
        "ENVIRONMENT": "staging",
        "ENABLE_SELF_SERVICE_TRIALS": "true",
        "ALLOW_DEV_LOGIN": "false",
        "DEMO_ENSURE_PROJECT": "false",
    }
    result = subprocess.run(
        [sys.executable, "-c", '''
from unittest.mock import patch
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from main import app
from database import engine
from auth.dependencies import get_current_user
from pathlib import Path
import sqlite3

for attempt in range(2):
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/auth/me").status_code in (401, 403)
        assert client.post("/auth/dev-login", json={"email": "john@fotonconsulting.com"}).status_code == 403
        assert client.post("/ai/fmea/suggest", json={}).status_code == 403
        with engine.begin() as conn:
            if attempt == 0:
                conn.execute(text("INSERT INTO users (id, email, plan) VALUES ('persisted', 'saved@example.com', 'lite')"))
            assert conn.execute(text("SELECT COUNT(*) FROM users WHERE id='persisted'")).scalar() == 1

with TestClient(app) as client:
    account = SimpleNamespace(id="persisted", plan="lite", trial_ends_at=datetime.now(timezone.utc) + timedelta(days=1),
                              subscription_status=None, stripe_customer_id=None, team_owner_id=None)
    app.dependency_overrides[get_current_user] = lambda: account
    # Active trial reaches request validation; expiry blocks the same direct API.
    assert client.post("/ai/fmea/suggest", json={}).status_code == 422
    account.trial_ends_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert client.post("/ai/fmea/suggest", json={}).status_code == 403
    assert client.get("/projects").status_code == 403
    assert client.get("/billing/status").status_code == 200
    app.dependency_overrides.clear()

snapshots = list((Path(engine.url.database).parent / "backups").glob("pre-schema-*.sqlite3"))
assert snapshots, "Restart must back up the existing database before schema changes"
with sqlite3.connect(snapshots[-1]) as snapshot:
    assert snapshot.execute("PRAGMA integrity_check").fetchone() == ("ok",)

inspector = inspect(engine)
assert {"trial_ends_at", "stripe_customer_id", "stripe_subscription_id", "team_owner_id"} <= {c["name"] for c in inspector.get_columns("users")}
assert {"billing_events", "team_invitations"} <= set(inspector.get_table_names())

with patch("schema_migrations.ensure_user_columns", side_effect=RuntimeError("migration unavailable")):
    try:
        with TestClient(app):
            raise AssertionError("Startup must reject an incomplete schema")
    except RuntimeError as exc:
        assert str(exc) == "migration unavailable"

with patch("schema_backup.backup_before_schema_change", side_effect=RuntimeError("backup unavailable")):
    try:
        with TestClient(app):
            raise AssertionError("Startup must stop if the required backup fails")
    except RuntimeError as exc:
        assert str(exc) == "backup unavailable"
'''],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
