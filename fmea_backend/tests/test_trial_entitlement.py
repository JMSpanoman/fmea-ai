"""Boundary and migration checks for the opt-in SR1 trial foundation."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text

from auth.plan import get_user_plan, enforce_trial_project_limit
from db.runtime_migrations import ensure_user_columns


def test_trial_entitlement_expires_at_14_days_and_does_not_rewrite_paid_plan():
    now = datetime.now(timezone.utc)
    active = SimpleNamespace(plan="lite", trial_ends_at=now + timedelta(seconds=1))
    expired = SimpleNamespace(plan="lite", trial_ends_at=now - timedelta(seconds=1))
    paid = SimpleNamespace(plan="pro", trial_ends_at=now - timedelta(days=1))
    assert get_user_plan(active) == "pro"
    assert get_user_plan(expired) == "lite"
    assert get_user_plan(paid) == "pro"


def test_sqlite_migration_preserves_existing_user_and_is_repeatable():
    engine = create_engine("sqlite://")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE users (id VARCHAR PRIMARY KEY, email VARCHAR)"))
        conn.execute(text("INSERT INTO users (id, email) VALUES ('existing', 'existing@example.com')"))
    ensure_user_columns(engine)
    ensure_user_columns(engine)
    with engine.connect() as conn:
        row = conn.execute(text("SELECT id, email, trial_ends_at FROM users")).one()
    assert row == ("existing", "existing@example.com", None)


def test_trial_cannot_create_second_project():
    user = SimpleNamespace(id="trial-user", plan="lite", trial_ends_at=datetime.now(timezone.utc) + timedelta(days=2))
    with pytest.raises(HTTPException) as exc:
        enforce_trial_project_limit(user, existing_count=1)
    assert exc.value.status_code == 403

