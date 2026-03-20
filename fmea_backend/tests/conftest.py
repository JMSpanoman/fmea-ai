"""Shared pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from services.risk_rule_engine_defaults import build_default_criteria_payload


@pytest.fixture(scope="session")
def pacemaker_criteria_dict() -> dict:
    """ISO-style 4×4 matrix + implantable pacemaker keyword / escalation rules (deterministic seed)."""
    return build_default_criteria_payload(include_pacemaker_rules=True)


@pytest.fixture(scope="session")
def pacemaker_criteria_from_json_file() -> dict:
    """Same payload as ``pacemaker_criteria_dict``, loaded from committed JSON (audit-friendly artifact)."""
    path = Path(__file__).resolve().parent / "fixtures" / "pacemaker_risk_criteria.json"
    return json.loads(path.read_text(encoding="utf-8"))
