# SmartQS Risk Schema Migration Summary

## Overview
This migration adds missing fields to align the database schema with the SmartQS Risk core schema specification.

## Migration File
**File**: `fmea_backend/migrations/add_smartqs_risk_schema_fields.sql`

## Fields Added

### 1. risk_items
- ✅ `risk_key` (VARCHAR(50)) - Unique per project identifier (e.g., R-001, R-002)
- ✅ `created_by` (VARCHAR(255)) - FK to users table

### 2. risk_item_versions
- ✅ `created_by` (VARCHAR(255)) - FK to users table
- ⚠️ `changed_by` remains for backward compatibility

### 3. risk_controls
- ✅ `control_key` (VARCHAR(50)) - Unique within risk item identifier (e.g., RC-001, RC-002)
- ✅ `created_by` (VARCHAR(255)) - FK to users table

### 4. approvals
- ✅ `project_id` (VARCHAR(255)) - Direct project reference

### 5. trace_links
- ✅ `rationale` (TEXT) - Justification for trace link

## Indexes Created

- `idx_risk_items_risk_key` (project_id, risk_key)
- `idx_risk_item_versions_created_by` (created_by)
- `idx_risk_controls_control_key` (risk_item_id, control_key)
- `idx_risk_controls_created_by` (created_by)
- `idx_approvals_project_id` (project_id)
- `idx_trace_links_downstream` (project_id, from_type, from_id)
- `idx_trace_links_upstream` (project_id, to_type, to_id)

## Model Updates

### Updated Models
1. **risk_item.py** - Added `risk_key` and `created_by` fields with relationships
2. **risk_item_version.py** - Added `created_by` field with relationship
3. **risk_control.py** - Added `control_key` and `created_by` fields with relationships
4. **approval.py** - Added `project_id` field with relationship
5. **trace_link.py** - Added `rationale` field

## CRUD Function Updates

### Auto-Generation Functions
- `_generate_risk_key()` - Generates unique risk_key per project (R-001, R-002, ...)
- `_generate_control_key()` - Generates unique control_key per risk item (RC-001, RC-002, ...)

### Updated CRUD Functions
1. **risk_item.py**
   - `create_risk_item()` - Now accepts `created_by` parameter and auto-generates `risk_key`
   
2. **risk_item_version.py**
   - `create_risk_item_version()` - Now accepts `created_by` parameter

3. **risk_control.py**
   - `create_risk_control()` - Now accepts `created_by` parameter and auto-generates `control_key`

4. **approval_phase3.py**
   - `create_approval()` - Now sets `project_id` from ApprovalCreate schema

## Router Updates

### Updated Routers
- **risk_items.py**
  - `create_risk_item()` - Passes `current_user.id` as `created_by`
  - `create_risk_item_version()` - Passes `current_user.id` as `created_by`
  - `create_risk_control()` - Passes `current_user.id` as `created_by`
  - `approve_risk_item_version()` - Sets `project_id` in approval

## Schema Updates

### Updated Schemas
- **approval.py** - Added `project_id` field to `ApprovalCreate`

## Data Migration

The migration script includes logic to:
1. **Generate initial risk_key values** for existing risk_items (R-001, R-002, etc. per project)
2. **Generate initial control_key values** for existing risk_controls (RC-001, RC-002, etc. per risk_item)
3. **Populate project_id** in approvals by joining through artifact relationships
4. **Copy changed_by to created_by** in risk_item_versions (best-effort migration)

## Unique Constraints

⚠️ **Note**: SQLite doesn't support `ALTER TABLE ADD CONSTRAINT` for unique constraints. The migration creates indexes but unique constraints should be enforced at the application level.

For PostgreSQL, add:
```sql
ALTER TABLE risk_items ADD CONSTRAINT uq_risk_items_project_key UNIQUE (project_id, risk_key);
ALTER TABLE risk_controls ADD CONSTRAINT uq_risk_controls_item_key UNIQUE (risk_item_id, control_key);
```

## Foreign Key Constraints

The migration adds columns but FK constraints should be added separately for PostgreSQL:
```sql
ALTER TABLE risk_items ADD CONSTRAINT fk_risk_items_created_by FOREIGN KEY (created_by) REFERENCES users(id);
ALTER TABLE risk_item_versions ADD CONSTRAINT fk_risk_item_versions_created_by FOREIGN KEY (created_by) REFERENCES users(id);
ALTER TABLE risk_controls ADD CONSTRAINT fk_risk_controls_created_by FOREIGN KEY (created_by) REFERENCES users(id);
```

## Testing Checklist

- [ ] Run migration script on test database
- [ ] Verify risk_key auto-generation works for new risk items
- [ ] Verify control_key auto-generation works for new risk controls
- [ ] Verify created_by is set correctly for new records
- [ ] Verify project_id is set correctly for new approvals
- [ ] Verify rationale can be set on trace_links
- [ ] Test backward compatibility with existing data
- [ ] Verify indexes are created correctly
- [ ] Test unique constraint enforcement at application level

## Next Steps

1. **Run the migration** on development/staging environment
2. **Test thoroughly** with existing and new data
3. **Update frontend** to display new fields (risk_key, control_key, created_by)
4. **Add validation** for unique constraints at application level
5. **Add FK constraints** in PostgreSQL production environment
6. **Update API documentation** to reflect new fields

## Backward Compatibility

✅ All changes are backward compatible:
- New fields are nullable
- Existing code continues to work
- Auto-generation ensures new records have keys
- Migration populates existing records with generated keys

