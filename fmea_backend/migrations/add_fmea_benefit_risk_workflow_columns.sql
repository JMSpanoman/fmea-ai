-- Structured benefit–risk analysis documentation + multi-party acceptance attestations.

ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS bra_clinical_benefit_documented BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS bra_benefit_vs_residual_risk_documented BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS bra_state_of_the_art_documented BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS bra_supporting_evidence_addressed BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS bra_approval_clinical_medical_recorded BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS bra_approval_quality_regulatory_recorded BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS bra_approval_design_authority_recorded BOOLEAN NOT NULL DEFAULT FALSE;
