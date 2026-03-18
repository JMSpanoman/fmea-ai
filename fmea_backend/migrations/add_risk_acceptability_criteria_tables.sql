-- Migration: Risk Acceptability Criteria report and config (ISO 14971)
-- Date: 2025-02-05

CREATE TABLE IF NOT EXISTS organization_risk_criteria_configs (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL DEFAULT 'default',
    severity_scale TEXT,
    probability_scale TEXT,
    risk_matrix TEXT,
    decision_rules TEXT,
    terminology_overrides TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS project_risk_criteria_overrides (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    severity_scale TEXT,
    probability_scale TEXT,
    risk_matrix TEXT,
    decision_rules TEXT,
    approved_by VARCHAR(255),
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_project_risk_criteria_overrides_project_id ON project_risk_criteria_overrides(project_id);

CREATE TABLE IF NOT EXISTS risk_acceptability_criteria (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    title VARCHAR(500),
    content_json TEXT,
    content_html TEXT,
    source_metadata TEXT,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(255),
    approved_by VARCHAR(255),
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_risk_acceptability_criteria_project_id ON risk_acceptability_criteria(project_id);
CREATE INDEX IF NOT EXISTS ix_risk_acceptability_criteria_status ON risk_acceptability_criteria(status);
