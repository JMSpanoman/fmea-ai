-- Migration: Risk Acceptability Criteria workflow/config enhancements
-- Adds section metadata, readiness scoring, rationale fields, workflow states, and template support.

ALTER TABLE risk_acceptability_criteria ADD COLUMN section_metadata TEXT;
ALTER TABLE risk_acceptability_criteria ADD COLUMN readiness_metrics TEXT;
ALTER TABLE risk_acceptability_criteria ADD COLUMN review_comments TEXT;
ALTER TABLE risk_acceptability_criteria ADD COLUMN approval_notes TEXT;
ALTER TABLE risk_acceptability_criteria ADD COLUMN rejection_reason TEXT;
ALTER TABLE risk_acceptability_criteria ADD COLUMN supersedes_id VARCHAR(255);
ALTER TABLE risk_acceptability_criteria ADD COLUMN sections_json TEXT;
ALTER TABLE risk_acceptability_criteria ADD COLUMN section_document_version INTEGER DEFAULT 1;

ALTER TABLE organization_risk_criteria_configs ADD COLUMN organization_id VARCHAR(255);
ALTER TABLE organization_risk_criteria_configs ADD COLUMN template_name VARCHAR(255);
ALTER TABLE organization_risk_criteria_configs ADD COLUMN severity_rationale TEXT;
ALTER TABLE organization_risk_criteria_configs ADD COLUMN probability_rationale TEXT;
ALTER TABLE organization_risk_criteria_configs ADD COLUMN matrix_rationale TEXT;
ALTER TABLE organization_risk_criteria_configs ADD COLUMN decision_rules_rationale TEXT;
ALTER TABLE organization_risk_criteria_configs ADD COLUMN overall_residual_risk_methods TEXT;
ALTER TABLE organization_risk_criteria_configs ADD COLUMN approval_policy TEXT;
ALTER TABLE organization_risk_criteria_configs ADD COLUMN is_approved BOOLEAN DEFAULT 0;
ALTER TABLE organization_risk_criteria_configs ADD COLUMN approved_by VARCHAR(255);
ALTER TABLE organization_risk_criteria_configs ADD COLUMN approved_at DATETIME;

ALTER TABLE project_risk_criteria_overrides ADD COLUMN terminology_overrides TEXT;
ALTER TABLE project_risk_criteria_overrides ADD COLUMN severity_rationale TEXT;
ALTER TABLE project_risk_criteria_overrides ADD COLUMN probability_rationale TEXT;
ALTER TABLE project_risk_criteria_overrides ADD COLUMN matrix_rationale TEXT;
ALTER TABLE project_risk_criteria_overrides ADD COLUMN decision_rules_rationale TEXT;
ALTER TABLE project_risk_criteria_overrides ADD COLUMN overall_residual_risk_methods TEXT;
ALTER TABLE project_risk_criteria_overrides ADD COLUMN workflow_state VARCHAR(50) DEFAULT 'draft';
ALTER TABLE project_risk_criteria_overrides ADD COLUMN approval_notes TEXT;
ALTER TABLE project_risk_criteria_overrides ADD COLUMN rejection_reason TEXT;

CREATE INDEX IF NOT EXISTS ix_project_risk_criteria_overrides_workflow_state ON project_risk_criteria_overrides(workflow_state);
