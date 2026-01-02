# SmartQS Design Schema Migration Summary

## Overview
This migration adds missing fields to align the database schema with the SmartQS Design core schema specification.

## Migration File
**File**: `fmea_backend/migrations/add_smartqs_design_schema_fields.sql`

## Fields Added

### 1. design_inputs
- ✅ `di_key` (VARCHAR(50)) - Optional stable key like DI-014
- ✅ `title` (VARCHAR(255)) - Title or name
- ✅ `requirement` (TEXT) - Requirement text (alias for text, kept for backward compatibility)
- ✅ `status` (VARCHAR(50)) - draft/approved/implemented/obsolete (default: 'draft')
- ✅ `created_by` (VARCHAR(255)) - FK to users table
- ✅ `updated_at` (DATETIME) - Update timestamp

**Note**: `text` field retained for backward compatibility. `requirement` is populated from `text` for existing records.

### 2. design_outputs
- ✅ `do_key` (VARCHAR(50)) - Optional stable key like DO-009
- ✅ `title` (VARCHAR(255)) - Title or name
- ✅ `description` (TEXT) - Description (alias for text, kept for backward compatibility)
- ✅ `document_ref` (VARCHAR(255)) - Optional pointer to controlled doc
- ✅ `status` (VARCHAR(50)) - Status (default: 'draft')
- ✅ `created_by` (VARCHAR(255)) - FK to users table
- ✅ `updated_at` (DATETIME) - Update timestamp

**Note**: `text` field retained for backward compatibility. `description` is populated from `text` for existing records.

### 3. vv_tests
- ✅ `vv_key` (VARCHAR(50)) - Optional stable key like V-007
- ✅ `name` (VARCHAR(255)) - Test name (separate from test_method)
- ✅ `status` (VARCHAR(50)) - Status (default: 'draft')
- ✅ `created_by` (VARCHAR(255)) - FK to users table
- ✅ `updated_at` (DATETIME) - Update timestamp

**Note**: `name` is populated from `test_method` for existing records if not provided.

## Indexes Created

### design_inputs
- `idx_design_inputs_di_key` (project_id, di_key)
- `idx_design_inputs_status` (status)
- `idx_design_inputs_created_by` (created_by)

### design_outputs
- `idx_design_outputs_do_key` (project_id, do_key)
- `idx_design_outputs_status` (status)
- `idx_design_outputs_created_by` (created_by)

### vv_tests
- `idx_vv_tests_vv_key` (project_id, vv_key)
- `idx_vv_tests_status` (status)
- `idx_vv_tests_created_by` (created_by)

## Model Updates

### Updated Models
1. **design_input.py** - Added `di_key`, `title`, `requirement`, `status`, `created_by`, `updated_at` fields with relationships
2. **design_output.py** - Added `do_key`, `title`, `description`, `document_ref`, `status`, `created_by`, `updated_at` fields with relationships
3. **vv_test.py** - Added `vv_key`, `name`, `status`, `created_by`, `updated_at` fields with relationships

## CRUD Function Updates

### Auto-Generation Functions
- `_generate_di_key()` - Generates unique di_key per project (DI-001, DI-002, ...)
- `_generate_do_key()` - Generates unique do_key per project (DO-001, DO-002, ...)
- `_generate_vv_key()` - Generates unique vv_key per project (V-001, V-002, ...)

### Updated CRUD Functions
1. **design_control.py**
   - `create_design_input()` - Now accepts `created_by` parameter and auto-generates `di_key`
   - `create_design_output()` - Now accepts `created_by` parameter and auto-generates `do_key`
   
2. **vv.py**
   - `create_vv_test()` - Now accepts `created_by` parameter and auto-generates `vv_key`

## Router Updates

### Updated Routers
- **design_controls.py**
  - `create_design_input()` - Passes `current_user.id` as `created_by`
  - `create_design_output()` - Passes `current_user.id` as `created_by`

- **vv.py**
  - `create_vv_test()` - Passes `current_user.id` as `created_by`

- **risk_items.py**
  - `handoff_control_to_design()` - Passes `current_user.id` as `created_by` when creating design artifacts

- **ai_phase2.py**
  - `generate_design_controls()` - Passes `current_user.id` as `created_by` when creating design inputs/outputs

## Data Migration

The migration script includes logic to:
1. **Generate initial di_key values** for existing design_inputs (DI-001, DI-002, etc. per project)
2. **Generate initial do_key values** for existing design_outputs (DO-001, DO-002, etc. per project)
3. **Generate initial vv_key values** for existing vv_tests (V-001, V-002, etc. per project)
4. **Copy text to requirement** in design_inputs for backward compatibility
5. **Copy text to description** in design_outputs for backward compatibility
6. **Copy test_method to name** in vv_tests if name is not provided
7. **Set default status** to 'draft' for all records

## Unique Constraints

⚠️ **Note**: SQLite doesn't support `ALTER TABLE ADD CONSTRAINT` for unique constraints. The migration creates indexes but unique constraints should be enforced at the application level.

For PostgreSQL, add:
```sql
ALTER TABLE design_inputs ADD CONSTRAINT uq_design_inputs_project_key UNIQUE (project_id, di_key);
ALTER TABLE design_outputs ADD CONSTRAINT uq_design_outputs_project_key UNIQUE (project_id, do_key);
ALTER TABLE vv_tests ADD CONSTRAINT uq_vv_tests_project_key UNIQUE (project_id, vv_key);
```

## Foreign Key Constraints

The migration adds columns but FK constraints should be added separately for PostgreSQL:
```sql
ALTER TABLE design_inputs ADD CONSTRAINT fk_design_inputs_created_by FOREIGN KEY (created_by) REFERENCES users(id);
ALTER TABLE design_outputs ADD CONSTRAINT fk_design_outputs_created_by FOREIGN KEY (created_by) REFERENCES users(id);
ALTER TABLE vv_tests ADD CONSTRAINT fk_vv_tests_created_by FOREIGN KEY (created_by) REFERENCES users(id);
```

## Updated_at Triggers

The migration includes SQLite-compatible triggers for `updated_at`:
- `update_design_inputs_timestamp`
- `update_design_outputs_timestamp`
- `update_vv_tests_timestamp`

These triggers automatically update `updated_at` when records are modified.

## Traceability

The SmartQS Design schema maintains traceability through `trace_links`:

### Design-side canonical links:
- `risk_control → design_input` (link_type: `traces_to`)
- `design_input → design_output` (link_type: `traces_to`)
- `design_output → vv_test` (link_type: `verified_by`)
- `design_input → vv_test` (link_type: `verified_by`) - optional

### Critical indexes (already added in Risk migration):
- `(project_id, from_type, from_id)` → "what does this input/output link to?"
- `(project_id, to_type, to_id)` → "what is upstream of this output/test?"

## Testing Checklist

- [ ] Run migration script on test database
- [ ] Verify di_key auto-generation works for new design inputs
- [ ] Verify do_key auto-generation works for new design outputs
- [ ] Verify vv_key auto-generation works for new vv tests
- [ ] Verify created_by is set correctly for new records
- [ ] Verify status defaults to 'draft' for new records
- [ ] Verify updated_at triggers work correctly
- [ ] Test backward compatibility with existing data
- [ ] Verify indexes are created correctly
- [ ] Test traceability links work correctly
- [ ] Verify unique constraint enforcement at application level

## Next Steps

1. **Run the migration** on development/staging environment
2. **Test thoroughly** with existing and new data
3. **Update frontend** to display new fields (di_key, do_key, vv_key, title, status, created_by)
4. **Add validation** for unique constraints at application level
5. **Add FK constraints** in PostgreSQL production environment
6. **Update API documentation** to reflect new fields
7. **Update schemas** to include new fields in API responses

## Backward Compatibility

✅ All changes are backward compatible:
- New fields are nullable
- Existing `text` field retained in design_inputs and design_outputs
- Existing `test_method` field retained in vv_tests
- Auto-generation ensures new records have keys
- Migration populates existing records with generated keys
- Default status values set for existing records

## Schema Alignment

The schema now fully aligns with SmartQS Design core schema:
- ✅ design_inputs: All required fields present
- ✅ design_outputs: All required fields present
- ✅ vv_tests: All required fields present
- ✅ trace_links: Already updated with rationale in Risk migration
- ✅ Indexes: All critical indexes created

