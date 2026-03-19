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
    SOURCE_SYSTEM_DEFAULT,
    SOURCE_USER_EDITED,
    SOURCE_APPROVED_PROJECT,
    SOURCE_ORG_DEFAULT,
    _merge_with_existing_sections,
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
    assert "section_metadata" in report
    assert "readiness" in report
    assert "benefit_risk_workflow" in report
    assert "terminology" in report
    assert report["document_header"]["author_source"] == "SYSTEM-GENERATED DRAFT"


def test_build_report_includes_per_section_metadata_fields():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(db, "proj-1", "Test Project", profile=None, generated_by=None)
    purpose_meta = report["section_metadata"]["purpose"]
    assert "source_type" in purpose_meta
    assert "requires_human_review" in purpose_meta
    assert "completeness" in purpose_meta
    assert "approved_by" in purpose_meta
    assert "approved_at" in purpose_meta
    assert "last_updated_at" in purpose_meta


def test_traceability_warnings_added_when_docs_missing():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(db, "proj-1", "Test Project", profile=None, generated_by=None)
    warnings = report["traceability_references"]["warnings"]
    assert isinstance(warnings, list)
    assert any("not linked" in w.lower() for w in warnings)


def test_generation_no_config_uses_hardcoded_editable_defaults():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(db, "proj-1", "Test Project", profile=None, generated_by=None)
    ed = report.get("editable_defaults", {})
    assert ed["decision_rule_wording"]["current_value"]
    assert ed["decision_rule_wording"]["source_type"] == SOURCE_SYSTEM_DEFAULT
    assert ed["alarp_terminology"]["source_type"] == SOURCE_SYSTEM_DEFAULT


def test_org_override_beats_hardcoded_defaults_for_editable_fields():
    db = MagicMock()
    override = None
    org = MagicMock()
    org.severity_scale = None
    org.probability_scale = None
    org.risk_matrix = None
    org.decision_rules = "Org-specific decision rules"
    org.terminology_overrides = {"ALARP": "Org ALARP wording"}
    org.severity_rationale = "Org severity rationale"
    org.probability_rationale = "Org probability rationale"
    org.matrix_rationale = "Org matrix rationale"
    org.decision_rules_rationale = "Org decision rules rationale"
    # ordered calls: override/order_by, org/first, rmp/order_by
    db.query.return_value.filter.return_value.order_by.return_value.first.side_effect = [override, None]
    db.query.return_value.filter.return_value.first.side_effect = [org]
    merged, sources = get_merged_criteria(db, "proj-1")
    assert merged["decision_rules"] == "Org-specific decision rules"
    assert merged["terminology_overrides"]["ALARP"] == "Org ALARP wording"
    assert sources["decision_rules"] == SOURCE_ORG_DEFAULT
    assert sources["severity_rationale"] == SOURCE_ORG_DEFAULT


def test_user_edits_persist_after_regeneration_by_default():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    existing = {
        "editable_defaults": {
            "decision_rule_wording": {
                "current_value": "User edited decision wording",
                "source_type": SOURCE_USER_EDITED,
                "last_edited_by": "u1",
                "last_edited_at": "2026-02-05T00:00:00Z",
                "default_value": "Default decision wording",
            }
        }
    }
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(
            db, "proj-1", "Test Project", profile=None, generated_by=None,
            existing_report=existing, regenerate_using_defaults=False
        )
    assert report["editable_defaults"]["decision_rule_wording"]["current_value"] == "User edited decision wording"
    assert report["editable_defaults"]["decision_rule_wording"]["source_type"] == SOURCE_USER_EDITED


def test_forced_regeneration_replaces_default_derived_content():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    existing = {
        "editable_defaults": {
            "decision_rule_wording": {
                "current_value": "Old default-derived value",
                "source_type": SOURCE_SYSTEM_DEFAULT,
                "last_edited_by": None,
                "last_edited_at": None,
                "default_value": "Another default",
            }
        }
    }
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(
            db, "proj-1", "Test Project", profile=None, generated_by=None,
            existing_report=existing, regenerate_using_defaults=True
        )
    assert report["editable_defaults"]["decision_rule_wording"]["current_value"] != "Old default-derived value"


def test_initial_generation_populates_structured_sections():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(db, "proj-1", "Test Project", profile=None, generated_by=None)
    sections = report.get("sections", {})
    for key in [
        "purpose", "scope", "regulatory_basis", "definitions", "severity_scale", "severity_rationale",
        "probability_scale", "probability_rationale", "alarp_terminology", "risk_matrix",
        "matrix_rationale", "decision_rule_wording", "decision_rules_rationale", "residual_risk_rules",
        "benefit_risk_triggers", "control_effectiveness", "overall_residual_risk",
        "roles_and_responsibilities", "traceability", "ai_transparency", "manual_review_items",
    ]:
        assert key in sections
        assert sections[key]["version"] == 1
        assert sections[key]["approved"] is False


def test_approved_section_not_overwritten_by_regeneration_merge():
    generated = {"purpose": {"key": "purpose", "value": "new", "approved": False, "is_user_edited": False, "version": 1}}
    existing = {"purpose": {"key": "purpose", "value": "locked", "approved": True, "is_user_edited": False, "version": 3}}
    merged = _merge_with_existing_sections(generated, existing)
    assert merged["purpose"]["value"] == "locked"
    assert merged["purpose"]["version"] == 3


def test_force_regenerate_ignores_existing_approved_sections():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    existing = {"sections": {"purpose": {"key": "purpose", "value": "locked", "approved": True, "is_user_edited": False, "version": 2}}}
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(db, "proj-1", "Test Project", profile=None, generated_by=None, existing_report=existing, regenerate_using_defaults=True)
    assert report["sections"]["purpose"]["value"] != "locked"


def test_section_source_type_updates_on_user_edited_merge():
    generated = {"scope": {"key": "scope", "value": "generated", "approved": False, "is_user_edited": False, "version": 1, "source_type": SOURCE_SYSTEM_DEFAULT}}
    existing = {"scope": {"key": "scope", "value": "custom", "approved": False, "is_user_edited": True, "version": 2, "source_type": SOURCE_USER_EDITED}}
    merged = _merge_with_existing_sections(generated, existing)
    assert merged["scope"]["source_type"] == SOURCE_USER_EDITED
    assert merged["scope"]["value"] == "custom"


def test_renderer_includes_new_sections_in_required_order():
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
        "purpose": {"text": "Purpose"},
        "scope": {"text": "Scope"},
        "regulatory_basis": {"text": "Reg"},
        "definitions": {"items": {}},
        "severity_scale": {"scale": []},
        "severity_rationale": {"text": "Severity rationale"},
        "probability_scale": {"scale": []},
        "probability_rationale": {"text": "Probability rationale"},
        "alarp_terminology": {"text": "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)"},
        "risk_matrix": {"matrix": []},
        "matrix_rationale": {"text": "Matrix rationale"},
        "decision_rule_wording": {"text": "Decision wording"},
        "decision_rules_rationale": {"text": "Decision rationale"},
        "decision_rules": {"text": "Decision wording", "rationale": "Decision rationale"},
        "residual_risk_rules": {"text": "Residual rules"},
        "benefit_risk_triggers": {"text": "Triggers"},
        "control_effectiveness_expectations": {"text": "Control"},
        "overall_residual_risk": {"text": "Overall"},
        "roles_and_responsibilities": {"roles": []},
        "review_and_approval": {"version_history": []},
        "traceability_references": {"items": {}, "warnings": []},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [],
    }
    html = render_risk_acceptability_criteria_html(report)
    expected_order = [
        "1. Purpose",
        "2. Scope",
        "3. Regulatory / standards basis",
        "4. Definitions",
        "5. Severity scale",
        "6. Severity rationale",
        "7. Probability scale",
        "8. Probability rationale",
        "9. ALARP terminology",
        "10. Risk acceptability matrix",
        "11. Matrix rationale",
        "12. Criteria interpretation / decision rules",
        "13. Decision rules rationale",
        "14. Residual risk evaluation rules",
        "15. Benefit-risk analysis trigger criteria",
        "16. Risk control effectiveness expectations",
        "17. Overall residual risk",
        "18. Roles and responsibilities",
        "19. Review and approval",
        "20. Traceability references",
        "21. AI / automation transparency",
        "22. Required manual review items",
    ]
    indices = [html.index(s) for s in expected_order]
    assert indices == sorted(indices)


def test_renderer_formats_multiline_and_bullets():
    report = {
        "document_header": {"project_name": "P", "project_id": "1"},
        "purpose": {"text": "P"},
        "scope": {"text": "S"},
        "regulatory_basis": {"text": "R"},
        "definitions": {"items": {}},
        "severity_scale": {"scale": []},
        "severity_rationale": {"text": "Para one.\n\n- item a\n- item b"},
        "probability_scale": {"scale": []},
        "probability_rationale": {"text": "Line one.\nLine two."},
        "alarp_terminology": {"text": "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)"},
        "risk_matrix": {"matrix": [["ALARP"]]},
        "matrix_rationale": {"text": "M"},
        "decision_rule_wording": {"text": "D"},
        "decision_rules_rationale": {"text": "DR"},
        "decision_rules": {"text": "D", "rationale": "DR"},
        "residual_risk_rules": {"text": "• A\n• B"},
        "benefit_risk_triggers": {"text": "• X\n• Y"},
        "control_effectiveness_expectations": {"text": "C"},
        "overall_residual_risk": {"text": "O"},
        "roles_and_responsibilities": {"roles": []},
        "review_and_approval": {"version_history": []},
        "traceability_references": {"items": {}, "warnings": []},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [],
    }
    html = render_risk_acceptability_criteria_html(report)
    assert html.count("<ul>") >= 2
    assert "<li>item a</li>" in html
    assert "<td>ALARP</td>" in html
    assert "<li>A</li>" in html
    assert "<li>X</li>" in html


def test_scope_uses_these_criteria_apply():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(db, "proj-1", "Test Project", profile=None, generated_by=None)
    assert report["scope"]["text"].startswith("These criteria apply")


def test_renderer_null_approval_fields_show_to_be_assigned():
    report = {
        "document_header": {"project_name": "P", "project_id": "1"},
        "purpose": {"text": "P"},
        "scope": {"text": "S"},
        "regulatory_basis": {"text": "R"},
        "definitions": {"items": {}},
        "severity_scale": {"scale": []},
        "severity_rationale": {"text": "SR"},
        "probability_scale": {"scale": []},
        "probability_rationale": {"text": "PR"},
        "alarp_terminology": {"text": "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)"},
        "risk_matrix": {"matrix": []},
        "matrix_rationale": {"text": "MR"},
        "decision_rule_wording": {"text": "D"},
        "decision_rules_rationale": {"text": "DR"},
        "decision_rules": {"text": "D", "rationale": "DR"},
        "residual_risk_rules": {"text": "Res"},
        "benefit_risk_triggers": {"text": "Trig"},
        "control_effectiveness_expectations": {"text": "C"},
        "overall_residual_risk": {"text": "O"},
        "roles_and_responsibilities": {"roles": []},
        "review_and_approval": {"prepared_by": None, "reviewed_by": None, "approved_by": None, "version_history": []},
        "traceability_references": {"items": {}, "warnings": []},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [],
    }
    html = render_risk_acceptability_criteria_html(report)
    assert "Prepared by: To be assigned" in html
    assert "Reviewed by: To be assigned" in html
    assert "Approved by: To be assigned" in html


def test_renderer_traceability_heading_and_dedup_manual_prefix():
    report = {
        "document_header": {"project_name": "P", "project_id": "1"},
        "purpose": {"text": "P"},
        "scope": {"text": "S"},
        "regulatory_basis": {"text": "R"},
        "definitions": {"items": {}},
        "severity_scale": {"scale": []},
        "severity_rationale": {"text": "SR"},
        "probability_scale": {"scale": []},
        "probability_rationale": {"text": "PR"},
        "alarp_terminology": {"text": "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)"},
        "risk_matrix": {"matrix": []},
        "matrix_rationale": {"text": "MR"},
        "decision_rule_wording": {"text": "D"},
        "decision_rules_rationale": {"text": "DR"},
        "decision_rules": {"text": "D", "rationale": "DR"},
        "residual_risk_rules": {"text": "Res"},
        "benefit_risk_triggers": {"text": "Trig"},
        "control_effectiveness_expectations": {"text": "C"},
        "overall_residual_risk": {"text": "O"},
        "roles_and_responsibilities": {"roles": []},
        "review_and_approval": {"version_history": []},
        "traceability_references": {"items": {}, "warnings": ["Risk Management Plan is not approved (status: draft)."]},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [{
            "section": "ALARP terminology",
            "message": "ALARP terminology: Confirm whether project or organization prefers “ALARP” or alternate terminology such as “Acceptable with Justification”.",
            "why_it_matters": "",
            "where_to_fix": "",
            "effect_on_approval_readiness": "",
        }],
    }
    html = render_risk_acceptability_criteria_html(report)
    assert "Traceability validation warnings" in html
    assert "Confirm whether project or organization prefers" in html
    assert "ALARP terminology: ALARP terminology:" not in html


def test_renderer_metadata_line_for_major_sections_and_readiness_blockers():
    report = {
        "document_header": {"project_name": "P", "project_id": "1"},
        "purpose": {"text": "P", "source_type": "system_draft", "requires_human_review": True, "approved_by": None},
        "scope": {"text": "S", "source_type": "system_draft", "requires_human_review": True, "approved_by": None},
        "regulatory_basis": {"text": "R", "source_type": "system_draft", "requires_human_review": True, "approved_by": None},
        "definitions": {"items": {}, "source_type": "system_draft", "requires_human_review": True, "approved_by": None},
        "severity_scale": {"scale": [], "source_type": "system_draft", "requires_human_review": True, "approved_by": None},
        "severity_rationale": {"text": "SR", "source_type": "system_default", "requires_human_review": True, "approved_by": None},
        "probability_scale": {"scale": [], "source_type": "system_draft", "requires_human_review": True, "approved_by": None},
        "probability_rationale": {"text": "PR", "source_type": "system_default", "requires_human_review": True, "approved_by": None},
        "alarp_terminology": {"text": "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)", "source_type": "system_default", "requires_human_review": True, "approved_by": None},
        "risk_matrix": {"matrix": [], "source_type": "system_draft", "requires_human_review": True, "approved_by": None},
        "matrix_rationale": {"text": "MR", "source_type": "system_default", "requires_human_review": True, "approved_by": None},
        "decision_rule_wording": {"text": "D", "source_type": "system_default", "requires_human_review": True, "approved_by": None},
        "decision_rules_rationale": {"text": "DR", "source_type": "system_default", "requires_human_review": True, "approved_by": None},
        "decision_rules": {"text": "D", "rationale": "DR"},
        "residual_risk_rules": {"text": "Res"},
        "benefit_risk_triggers": {"text": "Trig"},
        "control_effectiveness_expectations": {"text": "C"},
        "overall_residual_risk": {"text": "O"},
        "roles_and_responsibilities": {"roles": []},
        "review_and_approval": {"version_history": []},
        "traceability_references": {"items": {}, "warnings": []},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [],
        "readiness": {"completeness_percentage": 50, "approved_content_percentage": 10, "sections_requiring_manual_review": 4, "blocked_approval_reasons": ["a", "b"]},
    }
    html = render_risk_acceptability_criteria_html(report)
    assert "Source:" in html
    assert "Approval status:" in html
    assert "Human review required:" in html
    assert "Approved by:" in html
    assert "Approval blockers:</strong> 2" in html


def test_renderer_matrix_short_and_prose_expanded_alarp():
    report = {
        "document_header": {"project_name": "P", "project_id": "1"},
        "purpose": {"text": "P"},
        "scope": {"text": "S"},
        "regulatory_basis": {"text": "R"},
        "definitions": {"items": {}},
        "severity_scale": {"scale": []},
        "severity_rationale": {"text": "SR"},
        "probability_scale": {"scale": []},
        "probability_rationale": {"text": "PR"},
        "alarp_terminology": {"text": "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)"},
        "risk_matrix": {"matrix": [["ALARP"]]},
        "matrix_rationale": {"text": "Uses Acceptable with Justification (ALARP – As Low As Reasonably Practicable)."},
        "decision_rule_wording": {"text": "Uses Acceptable with Justification (ALARP – As Low As Reasonably Practicable)."},
        "decision_rules_rationale": {"text": "Uses Acceptable with Justification (ALARP – As Low As Reasonably Practicable)."},
        "decision_rules": {"text": "D", "rationale": "DR"},
        "residual_risk_rules": {"text": "When residual risk remains in \"Acceptable with Justification (ALARP – As Low As Reasonably Practicable)\", review is required."},
        "benefit_risk_triggers": {"text": "Trig"},
        "control_effectiveness_expectations": {"text": "C"},
        "overall_residual_risk": {"text": "O"},
        "roles_and_responsibilities": {"roles": []},
        "review_and_approval": {"version_history": []},
        "traceability_references": {"items": {}, "warnings": []},
        "ai_transparency": {"text": "AI"},
        "manual_review_items": [],
    }
    html = render_risk_acceptability_criteria_html(report)
    assert "<td>ALARP</td>" in html
    assert "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)" in html


def test_residual_risk_rules_use_selected_alarp_terminology():
    db = MagicMock()
    chain = MagicMock()
    chain.filter.return_value.order_by.return_value.first.return_value = None
    chain.filter.return_value.first.return_value = None
    db.query.return_value = chain
    existing = {
        "editable_defaults": {
            "alarp_terminology": {
                "current_value": "Conditionally acceptable with justification",
                "source_type": SOURCE_USER_EDITED,
                "last_edited_by": "u1",
                "last_edited_at": "2026-02-05T00:00:00Z",
                "default_value": "Acceptable with Justification (ALARP – As Low As Reasonably Practicable)",
            }
        }
    }
    with patch("crud.document.get_documents_by_project", return_value=[]):
        report = build_report(
            db, "proj-1", "Test Project", profile=None, generated_by=None,
            existing_report=existing, regenerate_using_defaults=False
        )
    assert "Conditionally acceptable with justification" in report["residual_risk_rules"]["text"]


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
