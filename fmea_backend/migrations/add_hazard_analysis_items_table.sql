-- Migration: Add hazard_analysis_items table (ISO 14971-style full hazard analysis)
-- Date: 2025-02-05
-- Description: Expanded hazard analysis schema for SmartRisk report with traceability

CREATE TABLE IF NOT EXISTS hazard_analysis_items (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    component_id VARCHAR(255),
    device_id VARCHAR(255),
    risk_item_id VARCHAR(255),
    risk_item_version_id VARCHAR(255),
    fmea_row_id VARCHAR(255),

    risk_key VARCHAR(50),
    version_no INTEGER NOT NULL DEFAULT 1,
    hazard_category VARCHAR(255),
    hazard TEXT,
    foreseeable_sequence_of_events TEXT,
    sequence_of_events TEXT,
    hazardous_situation TEXT,
    harm TEXT,
    affected_user VARCHAR(255),
    failure_mode TEXT,
    cause_of_failure TEXT,
    clinical_effect TEXT,
    operating_mode VARCHAR(255),
    use_environment TEXT,

    initial_severity INTEGER,
    initial_probability INTEGER,
    initial_occurrence INTEGER,
    initial_risk_level VARCHAR(50),

    risk_control_measures TEXT,
    risk_control_type TEXT,
    control_implementation_notes TEXT,
    risk_controls TEXT,

    residual_severity INTEGER,
    residual_probability INTEGER,
    residual_occurrence INTEGER,
    residual_risk_level VARCHAR(50),
    residual_risk_acceptability VARCHAR(100),
    risk_acceptability_decision VARCHAR(100),
    risk_acceptability_justification TEXT,
    benefit_risk_analysis_required BOOLEAN DEFAULT 0,
    benefit_risk_justification TEXT,

    related_design_input TEXT,
    related_design_output TEXT,
    verification_reference TEXT,
    validation_reference TEXT,
    capa_reference TEXT,
    requirement_ids TEXT,

    approval_status VARCHAR(50) DEFAULT 'draft',
    approved_by VARCHAR(255),
    approved_at DATETIME,
    approver_role VARCHAR(255),
    approval_meaning TEXT,
    version_lock BOOLEAN DEFAULT 0,
    review_date DATETIME,
    review_frequency VARCHAR(255),
    last_reviewed_by VARCHAR(255),
    post_market_trigger BOOLEAN DEFAULT 0,
    reviewer_comments TEXT,

    ai_generated INTEGER DEFAULT 0,
    ai_confidence VARCHAR(50),
    source_context TEXT,
    assumptions TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    created_by VARCHAR(255),

    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE SET NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL,
    FOREIGN KEY (risk_item_id) REFERENCES risk_items(id) ON DELETE SET NULL,
    FOREIGN KEY (risk_item_version_id) REFERENCES risk_item_versions(id) ON DELETE SET NULL,
    FOREIGN KEY (fmea_row_id) REFERENCES fmea_rows(id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (last_reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_project_id ON hazard_analysis_items(project_id);
CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_component_id ON hazard_analysis_items(component_id);
CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_device_id ON hazard_analysis_items(device_id);
CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_risk_item_id ON hazard_analysis_items(risk_item_id);
CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_approval_status ON hazard_analysis_items(approval_status);
CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_hazard_category ON hazard_analysis_items(hazard_category);
CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_last_reviewed_by ON hazard_analysis_items(last_reviewed_by);
