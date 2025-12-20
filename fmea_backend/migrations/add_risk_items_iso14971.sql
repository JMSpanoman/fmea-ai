-- Migration: Add ISO 14971 Risk Items Versioning and Controls
-- Date: 2024-01-20
-- Description: Add versioning, ISO 14971 fields, and risk controls to risk_items

-- Note: We add current_version_id column first, but the FK constraint will be added after risk_item_versions table is created
-- Add versioning field to risk_items
ALTER TABLE risk_items ADD COLUMN current_version_id VARCHAR(255);

-- Create risk_item_versions table (immutable snapshots)
CREATE TABLE IF NOT EXISTS risk_item_versions (
    id VARCHAR(255) PRIMARY KEY,
    risk_item_id VARCHAR(255) NOT NULL,
    version_number INTEGER NOT NULL DEFAULT 1,
    
    -- ISO 14971: Hazard analysis chain
    hazard TEXT,
    hazardous_situation TEXT,
    harm TEXT,
    failure_mode TEXT,
    sequence_of_events TEXT,
    
    -- Risk estimation (ISO 14971 compliant)
    severity INTEGER,
    probability_of_harm INTEGER,
    occurrence INTEGER,
    detection INTEGER,
    probability INTEGER,  -- Legacy
    impact INTEGER,  -- Legacy
    
    -- Calculated risk metrics
    risk_score INTEGER,
    risk_level VARCHAR(50),
    
    -- Risk control measures (ISO 14971)
    inherent_safety TEXT,
    protective_measures TEXT,
    information_for_safety TEXT,
    control_measures_summary TEXT,
    
    -- Residual risk evaluation (ISO 14971)
    residual_severity INTEGER,
    residual_probability_of_harm INTEGER,
    residual_occurrence INTEGER,
    residual_detection INTEGER,
    residual_risk_score INTEGER,
    residual_risk_level VARCHAR(50),
    
    -- Benefit-risk analysis (ISO 14971)
    benefit_risk_summary TEXT,
    overall_residual_risk_conclusion TEXT,
    
    -- Risk acceptability (ISO 14971)
    risk_acceptability VARCHAR(50),
    risk_rationale TEXT,
    
    -- Metadata
    change_summary TEXT,
    changed_by VARCHAR(255),
    ai_metadata TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (risk_item_id) REFERENCES risk_items(id) ON DELETE CASCADE
);

-- Create risk_controls table
CREATE TABLE IF NOT EXISTS risk_controls (
    id VARCHAR(255) PRIMARY KEY,
    risk_item_id VARCHAR(255) NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    
    -- Control identification
    control_name VARCHAR(255) NOT NULL,
    control_description TEXT,
    control_type VARCHAR(50) NOT NULL,  -- inherent_safety, protective, information
    
    -- Control details
    implementation_details TEXT,
    verification_method TEXT,
    trace_to_design_input VARCHAR(255),
    trace_to_design_output VARCHAR(255),
    trace_to_verification_test VARCHAR(255),
    
    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'proposed',  -- proposed, active, retired
    
    -- Ownership
    owner VARCHAR(255),
    assigned_to VARCHAR(255),
    
    -- Dates
    proposed_date DATETIME,
    implemented_date DATETIME,
    verified_date DATETIME,
    
    -- Metadata
    effectiveness_notes TEXT,
    ai_metadata TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    
    FOREIGN KEY (risk_item_id) REFERENCES risk_items(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Create index for current_version_id (FK constraint added separately if needed)
CREATE INDEX IF NOT EXISTS idx_risk_items_current_version ON risk_items(current_version_id);

-- For PostgreSQL: Add FK constraint (SQLite doesn't support ALTER TABLE ADD CONSTRAINT well)
-- Note: In production with PostgreSQL, you may want to add:
-- ALTER TABLE risk_items ADD CONSTRAINT fk_risk_items_current_version 
--     FOREIGN KEY (current_version_id) REFERENCES risk_item_versions(id) ON DELETE SET NULL;
-- This is skipped for SQLite compatibility.

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_risk_item_versions_risk_item ON risk_item_versions(risk_item_id);
CREATE INDEX IF NOT EXISTS idx_risk_item_versions_version_number ON risk_item_versions(risk_item_id, version_number);
CREATE INDEX IF NOT EXISTS idx_risk_controls_risk_item ON risk_controls(risk_item_id);
CREATE INDEX IF NOT EXISTS idx_risk_controls_project ON risk_controls(project_id);
CREATE INDEX IF NOT EXISTS idx_risk_controls_status ON risk_controls(status);
CREATE INDEX IF NOT EXISTS idx_risk_controls_type ON risk_controls(control_type);

-- For SQLite compatibility, handle updated_at with a trigger
CREATE TRIGGER IF NOT EXISTS update_risk_controls_timestamp 
    AFTER UPDATE ON risk_controls
    FOR EACH ROW
    BEGIN
        UPDATE risk_controls SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Note: Foreign key constraint for current_version_id would need to be added separately
-- in PostgreSQL, but SQLite doesn't support deferred FK constraints well.
-- Application code should ensure referential integrity.

