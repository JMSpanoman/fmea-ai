-- Migration: Add Version Control Tables
-- Date: 2024-01-15
-- Description: Add comprehensive version control system for all documents and reports

-- Create document_versions table
CREATE TABLE IF NOT EXISTS document_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_type VARCHAR(100) NOT NULL,
    document_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    version_number VARCHAR(20) NOT NULL,
    major_version INTEGER NOT NULL DEFAULT 1,
    minor_version INTEGER NOT NULL DEFAULT 0,
    patch_version INTEGER NOT NULL DEFAULT 0,
    version_label VARCHAR(100),
    version_status VARCHAR(50) NOT NULL DEFAULT 'draft',
    change_type VARCHAR(50),
    content_hash VARCHAR(64) NOT NULL,
    content_snapshot TEXT,
    file_path VARCHAR(500),
    change_summary TEXT,
    change_details TEXT,
    approval_required VARCHAR(10) DEFAULT 'false',
    approved_by VARCHAR(255),
    approved_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create version_history table
CREATE TABLE IF NOT EXISTS version_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_version_id INTEGER NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    change_type VARCHAR(50) NOT NULL,
    changed_by VARCHAR(255) NOT NULL,
    change_reason TEXT,
    change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_version_id) REFERENCES document_versions(id)
);

-- Create document_templates table
CREATE TABLE IF NOT EXISTS document_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name VARCHAR(255) NOT NULL,
    template_type VARCHAR(100) NOT NULL,
    template_category VARCHAR(100),
    version_number VARCHAR(20) NOT NULL DEFAULT '1.0',
    is_active BOOLEAN DEFAULT 1,
    is_default BOOLEAN DEFAULT 0,
    template_file_path VARCHAR(500),
    template_content TEXT,
    template_metadata TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) NOT NULL
);

-- Create document_exports table
CREATE TABLE IF NOT EXISTS document_exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_type VARCHAR(100) NOT NULL,
    document_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    version_number VARCHAR(20) NOT NULL,
    export_format VARCHAR(50) NOT NULL,
    export_filename VARCHAR(255) NOT NULL,
    export_file_path VARCHAR(500),
    export_file_size INTEGER,
    export_hash VARCHAR(64),
    export_settings TEXT,
    export_notes TEXT,
    exported_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_document_versions_type_id ON document_versions(document_type, document_id);
CREATE INDEX IF NOT EXISTS idx_document_versions_project ON document_versions(project_id);
CREATE INDEX IF NOT EXISTS idx_document_versions_user ON document_versions(user_id);
CREATE INDEX IF NOT EXISTS idx_document_versions_status ON document_versions(version_status);
CREATE INDEX IF NOT EXISTS idx_document_versions_created ON document_versions(created_at);

CREATE INDEX IF NOT EXISTS idx_version_history_version ON version_history(document_version_id);
CREATE INDEX IF NOT EXISTS idx_version_history_timestamp ON version_history(change_timestamp);

CREATE INDEX IF NOT EXISTS idx_document_templates_type ON document_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_document_templates_active ON document_templates(is_active);

CREATE INDEX IF NOT EXISTS idx_document_exports_type_id ON document_exports(document_type, document_id);
CREATE INDEX IF NOT EXISTS idx_document_exports_project ON document_exports(project_id);
CREATE INDEX IF NOT EXISTS idx_document_exports_format ON document_exports(export_format);
CREATE INDEX IF NOT EXISTS idx_document_exports_timestamp ON document_exports(exported_at);

-- Add version control fields to existing tables
-- FMEA table
ALTER TABLE fmea_entries ADD COLUMN version_number VARCHAR(20) DEFAULT '1.0';
ALTER TABLE fmea_entries ADD COLUMN major_version INTEGER DEFAULT 1;
ALTER TABLE fmea_entries ADD COLUMN minor_version INTEGER DEFAULT 0;
ALTER TABLE fmea_entries ADD COLUMN patch_version INTEGER DEFAULT 0;
ALTER TABLE fmea_entries ADD COLUMN version_status VARCHAR(50) DEFAULT 'draft';
ALTER TABLE fmea_entries ADD COLUMN version_label VARCHAR(100);
ALTER TABLE fmea_entries ADD COLUMN change_summary TEXT;
ALTER TABLE fmea_entries ADD COLUMN change_details TEXT;
ALTER TABLE fmea_entries ADD COLUMN content_hash VARCHAR(64);
ALTER TABLE fmea_entries ADD COLUMN approval_required VARCHAR(10) DEFAULT 'false';
ALTER TABLE fmea_entries ADD COLUMN approved_by VARCHAR(255);
ALTER TABLE fmea_entries ADD COLUMN approved_at DATETIME;
ALTER TABLE fmea_entries ADD COLUMN version_created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE fmea_entries ADD COLUMN version_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Projects table
ALTER TABLE projects ADD COLUMN version_number VARCHAR(20) DEFAULT '1.0';
ALTER TABLE projects ADD COLUMN major_version INTEGER DEFAULT 1;
ALTER TABLE projects ADD COLUMN minor_version INTEGER DEFAULT 0;
ALTER TABLE projects ADD COLUMN patch_version INTEGER DEFAULT 0;
ALTER TABLE projects ADD COLUMN version_status VARCHAR(50) DEFAULT 'draft';
ALTER TABLE projects ADD COLUMN version_label VARCHAR(100);
ALTER TABLE projects ADD COLUMN change_summary TEXT;
ALTER TABLE projects ADD COLUMN change_details TEXT;
ALTER TABLE projects ADD COLUMN content_hash VARCHAR(64);
ALTER TABLE projects ADD COLUMN approval_required VARCHAR(10) DEFAULT 'false';
ALTER TABLE projects ADD COLUMN approved_by VARCHAR(255);
ALTER TABLE projects ADD COLUMN approved_at DATETIME;
ALTER TABLE projects ADD COLUMN version_created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE projects ADD COLUMN version_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Insert sample data for testing
INSERT INTO document_templates (template_name, template_type, template_category, created_by) VALUES
('FMEA Standard Template', 'fmea', 'general', 'system'),
('CAPA Standard Template', 'capa', 'general', 'system'),
('Risk Management Template', 'risk_report', 'general', 'system'),
('Medical Device FMEA', 'fmea', 'medical', 'system'),
('Automotive FMEA', 'fmea', 'automotive', 'system'),
('Aerospace FMEA', 'fmea', 'aerospace', 'system');

-- Create triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_document_versions_timestamp 
    AFTER UPDATE ON document_versions
    FOR EACH ROW
    BEGIN
        UPDATE document_versions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_document_templates_timestamp 
    AFTER UPDATE ON document_templates
    FOR EACH ROW
    BEGIN
        UPDATE document_templates SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

-- Create view for easy access to latest versions
CREATE VIEW IF NOT EXISTS latest_document_versions AS
SELECT 
    dv.*,
    ROW_NUMBER() OVER (
        PARTITION BY dv.document_type, dv.document_id, dv.project_id 
        ORDER BY dv.major_version DESC, dv.minor_version DESC, dv.patch_version DESC
    ) as version_rank
FROM document_versions dv;

-- Create view for document version summary
CREATE VIEW IF NOT EXISTS document_version_summary AS
SELECT 
    document_type,
    document_id,
    project_id,
    COUNT(*) as total_versions,
    MAX(version_number) as latest_version,
    MAX(CASE WHEN version_status = 'published' THEN version_number END) as published_version,
    MAX(CASE WHEN version_status = 'approved' THEN version_number END) as approved_version,
    MAX(created_at) as last_updated
FROM document_versions
GROUP BY document_type, document_id, project_id;
