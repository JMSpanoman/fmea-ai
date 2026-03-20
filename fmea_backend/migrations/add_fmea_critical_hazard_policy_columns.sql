-- Critical hazard policy attestations + aggregates (implantable pacemaker / life-sustaining workflows).

ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS critical_hazard_severity_floor_waived BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS risk_eliminated BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS system_level_verification_recorded BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS critical_hazard_category_flag BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS system_level_verification_required BOOLEAN NOT NULL DEFAULT FALSE;
