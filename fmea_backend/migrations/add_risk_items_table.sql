-- Migration: Add Risk Items Table
-- Date: 2024-01-20
-- Description: Add comprehensive risk items management table for SmartQS Risk

-- Create risk_items table
CREATE TABLE IF NOT EXISTS risk_items (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    fmea_row_id VARCHAR(255),
    
    -- Risk identification
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    risk_type VARCHAR(255),
    
    -- Risk assessment
    severity INTEGER,
    probability INTEGER,
    impact INTEGER,
    risk_score INTEGER,
    risk_level VARCHAR(50),
    
    -- Risk control
    mitigation_strategy TEXT,
    control_measures TEXT,
    residual_risk_score INTEGER,
    residual_risk_level VARCHAR(50),
    
    -- Ownership and status
    owner VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    priority VARCHAR(50),
    
    -- Additional metadata
    source VARCHAR(255),
    detected_date DATETIME,
    due_date DATETIME,
    closed_date DATETIME,
    
    -- AI and metadata
    ai_metadata TEXT,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (fmea_row_id) REFERENCES fmea_rows(id) ON DELETE SET NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_risk_items_project ON risk_items(project_id);
CREATE INDEX IF NOT EXISTS idx_risk_items_fmea_row ON risk_items(fmea_row_id);
CREATE INDEX IF NOT EXISTS idx_risk_items_status ON risk_items(status);
CREATE INDEX IF NOT EXISTS idx_risk_items_category ON risk_items(category);
CREATE INDEX IF NOT EXISTS idx_risk_items_risk_level ON risk_items(risk_level);
CREATE INDEX IF NOT EXISTS idx_risk_items_created_at ON risk_items(created_at);

-- For SQLite compatibility, handle updated_at with a trigger
CREATE TRIGGER IF NOT EXISTS update_risk_items_timestamp 
    AFTER UPDATE ON risk_items
    FOR EACH ROW
    BEGIN
        UPDATE risk_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

