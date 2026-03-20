-- Postgres-oriented DDL for risk acceptability rule engine (FMEA).
-- Run manually if your deployment does not rely on SQLAlchemy create_all + SQLite runtime migrations.

CREATE TABLE IF NOT EXISTS project_risk_criteria (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id),
    version INTEGER NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    evaluation_method VARCHAR(32) NOT NULL DEFAULT 'matrix',
    severity_scale JSONB,
    probability_scale JSONB,
    detection_scale JSONB,
    risk_matrix JSONB,
    score_thresholds JSONB,
    special_rules JSONB,
    approval_metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_project_risk_criteria_project_id ON project_risk_criteria(project_id);
CREATE INDEX IF NOT EXISTS ix_project_risk_criteria_status ON project_risk_criteria(status);

CREATE TABLE IF NOT EXISTS rule_evaluation_audits (
    id VARCHAR PRIMARY KEY,
    fmea_row_id VARCHAR NOT NULL REFERENCES fmea_rows(id) ON DELETE CASCADE,
    project_id VARCHAR NOT NULL REFERENCES projects(id),
    criteria_version INTEGER NOT NULL,
    evaluation_type VARCHAR(32) NOT NULL,
    inputs_json JSONB,
    matched_rules_json JSONB,
    output_json JSONB,
    decision_path_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_rule_audit_fmea_row ON rule_evaluation_audits(fmea_row_id);
CREATE INDEX IF NOT EXISTS ix_rule_audit_project ON rule_evaluation_audits(project_id);

-- FMEA row extensions (skip any column that already exists)
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS device_function TEXT;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS hazard TEXT;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS harm TEXT;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS action_taken TEXT;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS initial_risk_classification VARCHAR(32);
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS residual_risk_classification VARCHAR(32);
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS benefit_risk_required BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS reviewer_justification TEXT;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS reviewer_name VARCHAR(255);
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS reviewer_date TIMESTAMPTZ;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS critical_function_flag BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS approval_blocked BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS rule_engine_result_json JSONB;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS ai_suggested_values_json JSONB;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS risk_criteria_version_applied INTEGER;
