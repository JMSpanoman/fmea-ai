"""Tests: PMS plan MAUDE simulation, normalization, persistence, HTML export."""
from __future__ import annotations

import hashlib
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models.pms_generated_plan import PmsGeneratedPlan
from models.project import Project
from models.user import User
from crud.pms_generated_plan import (
    create_pms_generated_plan,
    get_pms_generated_plan,
    list_pms_generated_plans_by_project,
    next_plan_version,
)
from services.maude_signal_provider import SimulatedMaudeSignalProvider, set_maude_signal_provider
from services.pms_plan_generator_service import (
    REQUIRED_SECTION_KEYS,
    _normalize_plan_dict,
    build_pms_plan_printable_html,
    get_pms_plan_for_user,
    list_pms_plans_merged,
)
from schemas.pms_plan import MaudeSignalPublic, PmsPlanHistoryItem, PmsPlanSections


@pytest.fixture()
def memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Sess = sessionmaker(bind=engine)
    db = Sess()
    uid = str(uuid.uuid4())
    pid = str(uuid.uuid4())
    db.add(User(id=uid, email="t@example.com", plan="pro"))
    db.add(Project(id=pid, user_id=uid, name="P1"))
    db.commit()
    try:
        yield db, uid, pid
    finally:
        db.close()


def test_simulated_maude_deterministic_sha256():
    p = SimulatedMaudeSignalProvider()
    fmea = [
        {"failure_mode": "Battery depletion"},
        {"failure_mode": "Battery depletion"},
        {"failure_mode": "Lead fracture"},
    ]
    a = p.get_signals(project_id="proj-1", device_name="D", intended_use="U", fmea_rows=fmea)
    b = p.get_signals(project_id="proj-1", device_name="D", intended_use="U", fmea_rows=fmea)
    assert a == b
    assert len(a) >= 3
    assert all("recommended_monitoring_focus" in s for s in a)


def test_simulated_maude_cross_process_determinism():
    """Same seed string → same digest-based fields (not Python hash())."""
    p = SimulatedMaudeSignalProvider()
    fmea = [{"failure_mode": "Software reset loop"}]
    s = p.get_signals(project_id="pid", device_name="Dev", intended_use="use", fmea_rows=fmea)[0]
    seed = "pid\0Software reset loop\0Dev\0fmea:0"
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12], 16) % 1_000_000
    assert s["trend"] == ("increasing", "stable", "decreasing")[h % 3]


def test_simulated_maude_empty_fmea_min_three():
    p = SimulatedMaudeSignalProvider()
    s = p.get_signals(project_id="p", device_name="D", intended_use="U", fmea_rows=[])
    assert len(s) >= 3
    assert all(x.get("source") == "simulated_maude_generic" for x in s)


def test_normalize_plan_dict_fills_keys():
    raw = {"device_overview": "x"}
    out = _normalize_plan_dict(raw)
    assert set(out.keys()) == set(REQUIRED_SECTION_KEYS)
    assert out["device_overview"] == "x"
    assert out["reporting"] == "—"


def test_persistence_crud(memory_db):
    db, uid, pid = memory_db
    gen_id = str(uuid.uuid4())
    payload = {
        "sections": {k: "s" for k in REQUIRED_SECTION_KEYS},
        "maude_signals": [],
        "fmea_row_count": 0,
        "model": "stub",
        "ai_generated": False,
        "warning": "w",
    }
    create_pms_generated_plan(
        db,
        generation_id=gen_id,
        project_id=pid,
        user_id=uid,
        device_name="Dev",
        intended_use="IU",
        summary="sum",
        status="draft",
        version=1,
        payload_json=payload,
    )
    row = get_pms_generated_plan(db, gen_id)
    assert row is not None
    assert row.device_name == "Dev"
    lst = list_pms_generated_plans_by_project(db, pid)
    assert len(lst) == 1
    assert next_plan_version(db, pid) == 2


def test_get_pms_plan_for_user_404_wrong_user(memory_db):
    db, uid, pid = memory_db
    gen_id = str(uuid.uuid4())
    create_pms_generated_plan(
        db,
        generation_id=gen_id,
        project_id=pid,
        user_id=uid,
        device_name="D",
        intended_use="U",
        summary=None,
        status="draft",
        version=1,
        payload_json={"sections": {k: "x" for k in REQUIRED_SECTION_KEYS}, "maude_signals": []},
    )
    assert get_pms_plan_for_user(db, user_id="other-user", generation_id=gen_id) is None


def test_get_pms_plan_for_user_ok(memory_db):
    db, uid, pid = memory_db
    gen_id = str(uuid.uuid4())
    sec = {k: f"v-{k}" for k in REQUIRED_SECTION_KEYS}
    create_pms_generated_plan(
        db,
        generation_id=gen_id,
        project_id=pid,
        user_id=uid,
        device_name="MyDevice",
        intended_use="Treat",
        summary="S",
        status="draft",
        version=3,
        payload_json={
            "sections": sec,
            "maude_signals": [
                {
                    "failure_mode": "X",
                    "event_count": 5,
                    "trend": "stable",
                    "severity": "low",
                    "recommended_monitoring_focus": "watch",
                }
            ],
            "fmea_row_count": 2,
            "model": "m",
            "ai_generated": True,
            "warning": None,
        },
    )
    item = get_pms_plan_for_user(db, user_id=uid, generation_id=gen_id)
    assert item is not None
    assert item.device_name == "MyDevice"
    assert item.intended_use == "Treat"
    assert item.version == 3
    assert item.plan.device_overview == "v-device_overview"


def test_list_merged_permission_denied(memory_db):
    db, uid, pid = memory_db
    with pytest.raises(PermissionError):
        list_pms_plans_merged(db, user_id=uid, project_id="nonexistent-project-id")


def test_list_merged(memory_db):
    db, uid, pid = memory_db
    gen_id = str(uuid.uuid4())
    create_pms_generated_plan(
        db,
        generation_id=gen_id,
        project_id=pid,
        user_id=uid,
        device_name="D",
        intended_use="U",
        summary=None,
        status="draft",
        version=1,
        payload_json={"sections": {k: "a" for k in REQUIRED_SECTION_KEYS}, "maude_signals": []},
    )
    res = list_pms_plans_merged(db, user_id=uid, project_id=pid)
    assert res.project_id == pid
    assert len(res.items) == 1


def test_html_export_contains_meta_and_table():
    plan = PmsPlanSections(**{k: f"Section {k}" for k in REQUIRED_SECTION_KEYS})
    item = PmsPlanHistoryItem(
        id="gid",
        project_id="pid",
        device_name="Dev",
        intended_use="IU",
        created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        summary="Quick summary",
        status="draft",
        version=1,
        plan=plan,
        maude_signals=[
            MaudeSignalPublic(
                failure_mode="FM",
                event_count=10,
                trend="stable",
                severity="medium",
                recommended_monitoring_focus="focus",
            )
        ],
        fmea_row_count=4,
        model="gpt-test",
        ai_generated=True,
        warning="W",
    )
    html = build_pms_plan_printable_html(item=item)
    assert "Quick summary" in html
    assert "MAUDE-like signals" in html
    assert "FM" in html
    assert "focus" in html
    assert "FMEA rows used" in html
    assert "gpt-test" in html
    assert "Section device_overview" in html
    assert "<h2>Device Overview</h2>" in html


def teardown_module():
    set_maude_signal_provider(None)
