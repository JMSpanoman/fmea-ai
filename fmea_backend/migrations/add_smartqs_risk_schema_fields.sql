-- Migration: Add SmartQS Risk Schema Fields
-- Date: 2024-01-21
-- Description: Add missing fields for SmartQS Risk core schema compliance
--              - risk_key and created_by for risk_items
--              - created_by for risk_item_versions
--              - control_key and created_by for risk_controls
--              - project_id for approvals
--              - rationale for trace_links

-- ============================================================================
-- 1. risk_items: Add risk_key and created_by
-- ============================================================================

-- Add risk_key column (unique per project identifier, e.g., R-023)
ALTER TABLE risk_items ADD COLUMN risk_key VARCHAR(50);

-- Add created_by column (FK to users)
ALTER TABLE risk_items ADD COLUMN created_by VARCHAR(255);

-- Generate initial risk_key values for existing records
-- Format: R-001, R-002, etc. per project
UPDATE risk_items 
SET risk_key = 'R-' || LPAD(
    CAST(
        (SELECT COUNT(*) + 1 
         FROM risk_items r2 
         WHERE r2.project_id = risk_items.project_id 
         AND r2.id < risk_items.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE risk_key IS NULL;

-- For records that couldn't be auto-numbered (first in each project)
UPDATE risk_items 
SET risk_key = 'R-' || LPAD(
    CAST(
        (SELECT COUNT(*) 
         FROM risk_items r2 
         WHERE r2.project_id = risk_items.project_id 
         AND r2.id <= risk_items.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE risk_key IS NULL;

-- Create index for risk_key lookups
CREATE INDEX IF NOT EXISTS idx_risk_items_risk_key ON risk_items(project_id, risk_key);

-- Note: Unique constraint (project_id, risk_key) should be enforced at application level
-- SQLite doesn't support ALTER TABLE ADD CONSTRAINT for unique constraints
-- For PostgreSQL, add: ALTER TABLE risk_items ADD CONSTRAINT uq_risk_items_project_key UNIQUE (project_id, risk_key);

-- ============================================================================
-- 2. risk_item_versions: Add created_by
-- ============================================================================

-- Add created_by column (FK to users)
-- Note: changed_by remains as String for backward compatibility
ALTER TABLE risk_item_versions ADD COLUMN created_by VARCHAR(255);

-- Copy changed_by to created_by for existing records (if changed_by looks like a UUID)
-- This is a best-effort migration - may need manual review
UPDATE risk_item_versions 
SET created_by = changed_by 
WHERE changed_by IS NOT NULL 
AND LENGTH(changed_by) = 36  -- UUID length
AND created_by IS NULL;

-- Create index for created_by lookups
CREATE INDEX IF NOT EXISTS idx_risk_item_versions_created_by ON risk_item_versions(created_by);

-- ============================================================================
-- 3. risk_controls: Add control_key and created_by
-- ============================================================================

-- Add control_key column (unique within a risk item, e.g., RC-003)
ALTER TABLE risk_controls ADD COLUMN control_key VARCHAR(50);

-- Add created_by column (FK to users)
ALTER TABLE risk_controls ADD COLUMN created_by VARCHAR(255);

-- Generate initial control_key values for existing records
-- Format: RC-001, RC-002, etc. per risk_item
UPDATE risk_controls 
SET control_key = 'RC-' || LPAD(
    CAST(
        (SELECT COUNT(*) + 1 
         FROM risk_controls rc2 
         WHERE rc2.risk_item_id = risk_controls.risk_item_id 
         AND rc2.id < risk_controls.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE control_key IS NULL;

-- For records that couldn't be auto-numbered (first in each risk_item)
UPDATE risk_controls 
SET control_key = 'RC-' || LPAD(
    CAST(
        (SELECT COUNT(*) 
         FROM risk_controls rc2 
         WHERE rc2.risk_item_id = risk_controls.risk_item_id 
         AND rc2.id <= risk_controls.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE control_key IS NULL;

-- Create index for control_key lookups
CREATE INDEX IF NOT EXISTS idx_risk_controls_control_key ON risk_controls(risk_item_id, control_key);

-- Create index for created_by lookups
CREATE INDEX IF NOT EXISTS idx_risk_controls_created_by ON risk_controls(created_by);

-- Note: Unique constraint (risk_item_id, control_key) should be enforced at application level
-- SQLite doesn't support ALTER TABLE ADD CONSTRAINT for unique constraints
-- For PostgreSQL, add: ALTER TABLE risk_controls ADD CONSTRAINT uq_risk_controls_item_key UNIQUE (risk_item_id, control_key);

-- ============================================================================
-- 4. approvals: Add project_id
-- ============================================================================

-- Add project_id column
ALTER TABLE approvals ADD COLUMN project_id VARCHAR(255);

-- Populate project_id from artifact relationships
-- For risk_item_version approvals, get project_id from risk_item_versions -> risk_items
UPDATE approvals 
SET project_id = (
    SELECT ri.project_id 
    FROM risk_item_versions riv
    JOIN risk_items ri ON riv.risk_item_id = ri.id
    WHERE riv.id = approvals.artifact_id
    AND approvals.artifact_type = 'risk_item_version'
)
WHERE project_id IS NULL 
AND artifact_type = 'risk_item_version';

-- For other artifact types, try to get project_id from their respective tables
-- Note: This is a best-effort migration - may need manual review for some records
UPDATE approvals 
SET project_id = (
    SELECT project_id FROM documents WHERE id = approvals.artifact_id
)
WHERE project_id IS NULL 
AND artifact_type = 'document';

UPDATE approvals 
SET project_id = (
    SELECT project_id FROM change_controls WHERE id = approvals.artifact_id
)
WHERE project_id IS NULL 
AND artifact_type = 'change_control';

UPDATE approvals 
SET project_id = (
    SELECT project_id FROM ncrs WHERE id = approvals.artifact_id
)
WHERE project_id IS NULL 
AND artifact_type = 'ncr';

UPDATE approvals 
SET project_id = (
    SELECT project_id FROM capas WHERE id = approvals.artifact_id
)
WHERE project_id IS NULL 
AND artifact_type = 'capa';

UPDATE approvals 
SET project_id = (
    SELECT project_id FROM audits WHERE id = approvals.artifact_id
)
WHERE project_id IS NULL 
AND artifact_type = 'audit';

UPDATE approvals 
SET project_id = (
    SELECT project_id FROM complaints WHERE id = approvals.artifact_id
)
WHERE project_id IS NULL 
AND artifact_type = 'complaint';

-- Create index for project_id lookups
CREATE INDEX IF NOT EXISTS idx_approvals_project_id ON approvals(project_id);

-- ============================================================================
-- 5. trace_links: Add rationale
-- ============================================================================

-- Add rationale column (justification for trace link)
ALTER TABLE trace_links ADD COLUMN rationale TEXT;

-- Create indexes for trace_links performance (as described in schema)
CREATE INDEX IF NOT EXISTS idx_trace_links_downstream ON trace_links(project_id, from_type, from_id);
CREATE INDEX IF NOT EXISTS idx_trace_links_upstream ON trace_links(project_id, to_type, to_id);

-- ============================================================================
-- Summary
-- ============================================================================

-- Fields added:
-- ✅ risk_items.risk_key (VARCHAR(50))
-- ✅ risk_items.created_by (VARCHAR(255))
-- ✅ risk_item_versions.created_by (VARCHAR(255))
-- ✅ risk_controls.control_key (VARCHAR(50))
-- ✅ risk_controls.created_by (VARCHAR(255))
-- ✅ approvals.project_id (VARCHAR(255))
-- ✅ trace_links.rationale (TEXT)

-- Indexes created:
-- ✅ idx_risk_items_risk_key (project_id, risk_key)
-- ✅ idx_risk_item_versions_created_by (created_by)
-- ✅ idx_risk_controls_control_key (risk_item_id, control_key)
-- ✅ idx_risk_controls_created_by (created_by)
-- ✅ idx_approvals_project_id (project_id)
-- ✅ idx_trace_links_downstream (project_id, from_type, from_id)
-- ✅ idx_trace_links_upstream (project_id, to_type, to_id)

-- Notes:
-- 1. Unique constraints should be enforced at application level for SQLite compatibility
-- 2. For PostgreSQL, add unique constraints:
--    - ALTER TABLE risk_items ADD CONSTRAINT uq_risk_items_project_key UNIQUE (project_id, risk_key);
--    - ALTER TABLE risk_controls ADD CONSTRAINT uq_risk_controls_item_key UNIQUE (risk_item_id, control_key);
-- 3. Foreign key constraints for created_by fields should be added if not already present:
--    - ALTER TABLE risk_items ADD CONSTRAINT fk_risk_items_created_by FOREIGN KEY (created_by) REFERENCES users(id);
--    - ALTER TABLE risk_item_versions ADD CONSTRAINT fk_risk_item_versions_created_by FOREIGN KEY (created_by) REFERENCES users(id);
--    - ALTER TABLE risk_controls ADD CONSTRAINT fk_risk_controls_created_by FOREIGN KEY (created_by) REFERENCES users(id);
-- 4. Some project_id values in approvals may need manual review if artifact relationships couldn't be determined

