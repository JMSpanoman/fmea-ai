-- Migration: Add SmartQS Design Schema Fields
-- Date: 2024-01-21
-- Description: Add missing fields for SmartQS Design core schema compliance
--              - di_key, title, status, created_by, updated_at for design_inputs
--              - do_key, title, document_ref, status, created_by, updated_at for design_outputs
--              - vv_key, name, status, created_by, updated_at for vv_tests

-- ============================================================================
-- 1. design_inputs: Add di_key, title, status, created_by, updated_at
-- ============================================================================

-- Add di_key column (optional stable key like DI-014)
ALTER TABLE design_inputs ADD COLUMN di_key VARCHAR(50);

-- Add title column (or name)
ALTER TABLE design_inputs ADD COLUMN title VARCHAR(255);

-- Rename text to requirement for clarity (or keep both)
-- Note: Keeping 'text' for backward compatibility, adding 'requirement' as alias
ALTER TABLE design_inputs ADD COLUMN requirement TEXT;

-- Copy text to requirement for existing records
UPDATE design_inputs SET requirement = text WHERE requirement IS NULL;

-- Add status column (draft/approved/implemented/obsolete)
ALTER TABLE design_inputs ADD COLUMN status VARCHAR(50) DEFAULT 'draft';

-- Add created_by column (FK to users)
ALTER TABLE design_inputs ADD COLUMN created_by VARCHAR(255);

-- Add updated_at column
ALTER TABLE design_inputs ADD COLUMN updated_at DATETIME;

-- Generate initial di_key values for existing records
-- Format: DI-001, DI-002, etc. per project
UPDATE design_inputs 
SET di_key = 'DI-' || LPAD(
    CAST(
        (SELECT COUNT(*) + 1 
         FROM design_inputs di2 
         WHERE di2.project_id = design_inputs.project_id 
         AND di2.id < design_inputs.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE di_key IS NULL;

-- For records that couldn't be auto-numbered (first in each project)
UPDATE design_inputs 
SET di_key = 'DI-' || LPAD(
    CAST(
        (SELECT COUNT(*) 
         FROM design_inputs di2 
         WHERE di2.project_id = design_inputs.project_id 
         AND di2.id <= design_inputs.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE di_key IS NULL;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_design_inputs_di_key ON design_inputs(project_id, di_key);
CREATE INDEX IF NOT EXISTS idx_design_inputs_status ON design_inputs(status);
CREATE INDEX IF NOT EXISTS idx_design_inputs_created_by ON design_inputs(created_by);

-- ============================================================================
-- 2. design_outputs: Add do_key, title, document_ref, status, created_by, updated_at
-- ============================================================================

-- Add do_key column (optional stable key like DO-009)
ALTER TABLE design_outputs ADD COLUMN do_key VARCHAR(50);

-- Add title column (or name)
ALTER TABLE design_outputs ADD COLUMN title VARCHAR(255);

-- Rename text to description for clarity (or keep both)
-- Note: Keeping 'text' for backward compatibility, adding 'description' as alias
ALTER TABLE design_outputs ADD COLUMN description TEXT;

-- Copy text to description for existing records
UPDATE design_outputs SET description = text WHERE description IS NULL;

-- Add document_ref column (optional pointer to controlled doc)
ALTER TABLE design_outputs ADD COLUMN document_ref VARCHAR(255);

-- Add status column
ALTER TABLE design_outputs ADD COLUMN status VARCHAR(50) DEFAULT 'draft';

-- Add created_by column (FK to users)
ALTER TABLE design_outputs ADD COLUMN created_by VARCHAR(255);

-- Add updated_at column
ALTER TABLE design_outputs ADD COLUMN updated_at DATETIME;

-- Generate initial do_key values for existing records
-- Format: DO-001, DO-002, etc. per project
UPDATE design_outputs 
SET do_key = 'DO-' || LPAD(
    CAST(
        (SELECT COUNT(*) + 1 
         FROM design_outputs do2 
         WHERE do2.project_id = design_outputs.project_id 
         AND do2.id < design_outputs.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE do_key IS NULL;

-- For records that couldn't be auto-numbered (first in each project)
UPDATE design_outputs 
SET do_key = 'DO-' || LPAD(
    CAST(
        (SELECT COUNT(*) 
         FROM design_outputs do2 
         WHERE do2.project_id = design_outputs.project_id 
         AND do2.id <= design_outputs.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE do_key IS NULL;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_design_outputs_do_key ON design_outputs(project_id, do_key);
CREATE INDEX IF NOT EXISTS idx_design_outputs_status ON design_outputs(status);
CREATE INDEX IF NOT EXISTS idx_design_outputs_created_by ON design_outputs(created_by);

-- ============================================================================
-- 3. vv_tests: Add vv_key, name, status, created_by, updated_at
-- ============================================================================

-- Add vv_key column (optional stable key like V-007)
ALTER TABLE vv_tests ADD COLUMN vv_key VARCHAR(50);

-- Add name column (separate from test_method)
ALTER TABLE vv_tests ADD COLUMN name VARCHAR(255);

-- Copy test_method to name for existing records (if name is empty)
UPDATE vv_tests SET name = test_method WHERE name IS NULL OR name = '';

-- Add status column
ALTER TABLE vv_tests ADD COLUMN status VARCHAR(50) DEFAULT 'draft';

-- Add created_by column (FK to users)
ALTER TABLE vv_tests ADD COLUMN created_by VARCHAR(255);

-- Add updated_at column
ALTER TABLE vv_tests ADD COLUMN updated_at DATETIME;

-- Generate initial vv_key values for existing records
-- Format: V-001, V-002, etc. per project
UPDATE vv_tests 
SET vv_key = 'V-' || LPAD(
    CAST(
        (SELECT COUNT(*) + 1 
         FROM vv_tests vv2 
         WHERE vv2.project_id = vv_tests.project_id 
         AND vv2.id < vv_tests.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE vv_key IS NULL;

-- For records that couldn't be auto-numbered (first in each project)
UPDATE vv_tests 
SET vv_key = 'V-' || LPAD(
    CAST(
        (SELECT COUNT(*) 
         FROM vv_tests vv2 
         WHERE vv2.project_id = vv_tests.project_id 
         AND vv2.id <= vv_tests.id) 
        AS INTEGER
    ), 
    3, 
    '0'
)
WHERE vv_key IS NULL;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_vv_tests_vv_key ON vv_tests(project_id, vv_key);
CREATE INDEX IF NOT EXISTS idx_vv_tests_status ON vv_tests(status);
CREATE INDEX IF NOT EXISTS idx_vv_tests_created_by ON vv_tests(created_by);

-- ============================================================================
-- Summary
-- ============================================================================

-- Fields added to design_inputs:
-- ✅ di_key (VARCHAR(50))
-- ✅ title (VARCHAR(255))
-- ✅ requirement (TEXT) - alias for text
-- ✅ status (VARCHAR(50))
-- ✅ created_by (VARCHAR(255))
-- ✅ updated_at (DATETIME)

-- Fields added to design_outputs:
-- ✅ do_key (VARCHAR(50))
-- ✅ title (VARCHAR(255))
-- ✅ description (TEXT) - alias for text
-- ✅ document_ref (VARCHAR(255))
-- ✅ status (VARCHAR(50))
-- ✅ created_by (VARCHAR(255))
-- ✅ updated_at (DATETIME)

-- Fields added to vv_tests:
-- ✅ vv_key (VARCHAR(50))
-- ✅ name (VARCHAR(255))
-- ✅ status (VARCHAR(50))
-- ✅ created_by (VARCHAR(255))
-- ✅ updated_at (DATETIME)

-- Indexes created:
-- ✅ idx_design_inputs_di_key (project_id, di_key)
-- ✅ idx_design_inputs_status (status)
-- ✅ idx_design_inputs_created_by (created_by)
-- ✅ idx_design_outputs_do_key (project_id, do_key)
-- ✅ idx_design_outputs_status (status)
-- ✅ idx_design_outputs_created_by (created_by)
-- ✅ idx_vv_tests_vv_key (project_id, vv_key)
-- ✅ idx_vv_tests_status (status)
-- ✅ idx_vv_tests_created_by (created_by)

-- Notes:
-- 1. Unique constraints should be enforced at application level for SQLite compatibility
-- 2. For PostgreSQL, add unique constraints:
--    - ALTER TABLE design_inputs ADD CONSTRAINT uq_design_inputs_project_key UNIQUE (project_id, di_key);
--    - ALTER TABLE design_outputs ADD CONSTRAINT uq_design_outputs_project_key UNIQUE (project_id, do_key);
--    - ALTER TABLE vv_tests ADD CONSTRAINT uq_vv_tests_project_key UNIQUE (project_id, vv_key);
-- 3. Foreign key constraints for created_by fields should be added if not already present:
--    - ALTER TABLE design_inputs ADD CONSTRAINT fk_design_inputs_created_by FOREIGN KEY (created_by) REFERENCES users(id);
--    - ALTER TABLE design_outputs ADD CONSTRAINT fk_design_outputs_created_by FOREIGN KEY (created_by) REFERENCES users(id);
--    - ALTER TABLE vv_tests ADD CONSTRAINT fk_vv_tests_created_by FOREIGN KEY (created_by) REFERENCES users(id);
-- 4. Updated_at triggers should be added for SQLite compatibility (see triggers below)

-- Add triggers for updated_at (SQLite compatibility)
CREATE TRIGGER IF NOT EXISTS update_design_inputs_timestamp 
    AFTER UPDATE ON design_inputs
    FOR EACH ROW
    BEGIN
        UPDATE design_inputs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_design_outputs_timestamp 
    AFTER UPDATE ON design_outputs
    FOR EACH ROW
    BEGIN
        UPDATE design_outputs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_vv_tests_timestamp 
    AFTER UPDATE ON vv_tests
    FOR EACH ROW
    BEGIN
        UPDATE vv_tests SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

