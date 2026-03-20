-- Mandatory release policy attestations + derived acceptable_for_release (FMEA rows).
-- Safe to run multiple times (IF NOT EXISTS).

ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS acceptable_for_release BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS benefit_risk_formal_approval_recorded BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS cross_functional_review_completed BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS formal_release_approval_recorded BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS additional_controls_reduced_risk BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS benefit_risk_analysis_approved BOOLEAN NOT NULL DEFAULT FALSE;
