"""
Tests for Risk Acceptability Criteria service: merge tiers, gap detection, report structure.
Also tests renderer: version history table (empty and non-empty).
"""
from unittest.mock import MagicMock, patch
from services.risk_acceptability_criteria_service import (
    get_merged_criteria,
    build_report,
    detect_gaps,
    SOURCE_SYSTEM_DRAFT,
    SOURCE_APPROVED_PROJECT,
    SOURCE_ORG_DEFAULT,
)
from business_logic.risk_acceptability_criteria_renderer import render_risk_acceptability_criteria_html


def test_get_merged_criteria_no_config_returns_system_draft():
    """With no project override and no org config, merged criteria use system draft."""
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    merged, sources = get_merged_criteria(db, "proj-1")
    assert "severity_scale" in merged
    assert "probability_scale" in merged
    assert "risk_matrix" in merged
    assert "decision_rules" in merged
    assert sources.get("severity_scale") == SOURCE_SYSTEM_DRAFT
    assert sources.get("probability_scale") == SOURCE_SYSTEM_DRAFT
    assert sources.get("risk_matrix") == SOURCE_SYSTEM_DRAFT


def test_detect_gaps_with_system_draft_reports_missing():
    """Gap detection flags missing approved scale and matrix when sources are system_draft."""
    db = MagicMock()
    section_sources = {
        "severity_scale": SOURCE_SYSTEM_DRAFT,
        "probability_scale": SOURCE_SYSTEM_DRAFT,
        "risk_matrix": SOURCE_SYSTEM_DRAFT,
    }
    report = {"traceability_references": {}}
    gaps = detect_gaps(db, "proj-1", "Test Project", None, section_sources, report)
    gap_ids = [g.get("id") for g in gaps]
    assert "severity_scale" in gap_ids
    assert "probability_scale" in gap_ids
    assert "risk_matrix" in gap_ids
    assert "approver" in gap_ids
    assert "residual_risk_doc" in gap_ids


def test_detect_gaps_residual_risk_doc_when_not_linked():
    """When traceability has no residual_risk_evaluation id, residual_risk_doc gap is added."""
    db = MagicMock()
    section_sources = {"severity_scale": SOURCE_ORG_DEFAULT}
    report = {
        "traceability_references": {
            "residual_risk_evaluation": {"id": None, "status": None},
        },
    }
    gaps = detect_gaps(db, "proj-1", "Test Project", None, section_sources, report)
    gap_ids = [g.get("id") for g in gaps]
    assert "residual_risk_doc" in gap_ids
    residual_gap = next(g for g in gaps if g.get("id") == "residual_risk_doc")
    assert "Residual Risk Evaluation" in residual_gap.get("message", "")
    assert residual_gap.get("section") == "Traceability references"


def test_detect_gaps_no_residual_risk_doc_gap_when_linked():
    """When residual_risk_evaluation has an id, residual_risk_doc gap is not added."""
    db = MagicMock()
    profile = MagicMock()
    profile.device_description = "Device"
    profile.intended_use = "Use"
    section_sources = {
        "severity_scale": SOURCE_ORG_DEFAULT,
        "probability_scale": SOURCE_ORG_DEFAULT,
        "risk_matrix": SOURCE_ORG_DEFAULT,
    }
    report = {
        "traceability_references": {
            "residual_risk_evaluation": {"id": "doc-123", "status": "draft"},
        },
    }
    gaps = detect_gaps(db, "proj-1", "Test Project", profile, section_sources, report)
    gap_ids = [g.get("id") for g in gaps]
    assert "residual_risk_doc" not in gap_ids


def test_build_report_has_all_sections():
    """Report dict contains all required sections for the document."""
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    profile = MagicMock()
    profile.device_description = "Test device"
    profile.intended_use = "Test use"
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(db, "proj-1", "Test Project", profile=profile, generated_by=None)
    assert "document_header" in report
    assert "purpose" in report
    assert "scope" in report
    assert "regulatory_basis" in report
    assert "definitions" in report
    assert "severity_scale" in report
    assert "probability_scale" in report
    assert "risk_matrix" in report
    assert "decision_rules" in report
    assert "residual_risk_rules" in report
    assert "benefit_risk_triggers" in report
    assert "control_effectiveness_expectations" in report
    assert "overall_residual_risk" in report
    assert "roles_and_responsibilities" in report
    assert "review_and_approval" in report
    assert "traceability_references" in report
    assert "ai_transparency" in report
    assert "manual_review_items" in report
    assert "source_metadata" in report
    assert report["document_header"]["author_source"] == "SYSTEM-GENERATED DRAFT"


def test_renderer_version_history_table_when_non_empty():
    """When version_history is non-empty, HTML contains the version history rows."""
    report = {
        "document_header": {
            "document_title": "Risk Acceptability Criteria",
            "project_name": "Test",
            "project_id": "p1",
            "device_name": "Device",
            "intended_use": "Use",
            "date_generated": "2025-02-05T12:00:00Z",
            "author_source": "SYSTEM-GENERATED DRAFT",
            "status": "draft",
            "version": 2,
        },
        "review_and_approval": {
            "prepared_by": "A",
            "reviewed_by": "B",
            "approved_by": "C",
            "version_history": [
                {"version": "1", "date": "2025-02-01", "description": "Initial", "author": "System"},
                {"version": "2", "date": "2025-02-05", "description": "Updated matrix", "author": "J. Smith"},
            ],
        },
        "purpose": {"text": "Purpose"},
        "scope": {"text": "Scope"},
        "regulatory_basis": {"text": "Reg"},
        "definitions": {"items": {}},
        "severity_scale": {"scale": [], "source_type": "system_draft"},
        "probability_scale": {"scale": [], "source_type": "system_draft"},
        "risk_matrix": {"matrix": [], "source_type": "system_draft"},
        "decision_rules": {"text": "Rules"},
        "residual_risk_rules": {"text": "Res"},
        "benefit_risk_triggers": {"text": "Triggers"},
        "control_effectiveness_expectations": {"text": "Control"},
        "overall_residual_risk": {"text": "Overall"},
        "roles_and_responsibilities": {"roles": []},
        "traceability_references": {},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [],
        "source_metadata": {},
    }
    html = render_risk_acceptability_criteria_html(report)
    assert "Version history" in html
    assert "2" in html
    assert "2025-02-05" in html
    assert "Updated matrix" in html
    assert "J. Smith" in html
    assert "1" in html
    assert "Initial" in html


def test_renderer_version_history_table_when_empty():
    """When version_history is empty, HTML contains default row (Initial draft, System)."""
    report = {
        "document_header": {
            "document_title": "Risk Acceptability Criteria",
            "project_name": "Test",
            "project_id": "p1",
            "device_name": "Device",
            "intended_use": "Use",
            "date_generated": "2025-02-05T12:00:00Z",
            "author_source": "SYSTEM-GENERATED DRAFT",
            "status": "draft",
            "version": 1,
        },
        "review_and_approval": {
            "prepared_by": "To be assigned",
            "reviewed_by": "To be assigned",
            "approved_by": "To be assigned",
            "version_history": [],
        },
        "purpose": {"text": "Purpose"},
        "scope": {"text": "Scope"},
        "regulatory_basis": {"text": "Reg"},
        "definitions": {"items": {}},
        "severity_scale": {"scale": [], "source_type": "system_draft"},
        "probability_scale": {"scale": [], "source_type": "system_draft"},
        "risk_matrix": {"matrix": [], "source_type": "system_draft"},
        "decision_rules": {"text": "Rules"},
        "residual_risk_rules": {"text": "Res"},
        "benefit_risk_triggers": {"text": "Triggers"},
        "control_effectiveness_expectations": {"text": "Control"},
        "overall_residual_risk": {"text": "Overall"},
        "roles_and_responsibilities": {"roles": []},
        "traceability_references": {},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [],
        "source_metadata": {},
    }
    html = render_risk_acceptability_criteria_html(report)
    assert "Version history" in html
    assert "Initial draft" in html
    assert "System" in html
