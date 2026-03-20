-- Project-level attestations for overall residual risk acceptability (ISO 14971 RMF / RMR).
-- Apply on Postgres when not relying solely on SQLAlchemy create_all.

ALTER TABLE project_profiles ADD COLUMN IF NOT EXISTS overall_device_benefit_risk_profile_acceptable BOOLEAN;
ALTER TABLE project_profiles ADD COLUMN IF NOT EXISTS rmr_overall_residual_risk_conclusion_documented BOOLEAN;
