-- Migration: Hazard Analysis regulatory-grade extensions (ISO 14971 alignment)
-- Adds full hazard-chain aliases, richer risk evaluation, structured controls,
-- traceability links, benefit-risk hooks, lifecycle metadata, and approval metadata.

ALTER TABLE hazard_analysis_items ADD COLUMN sequence_of_events TEXT;
ALTER TABLE hazard_analysis_items ADD COLUMN initial_occurrence INTEGER;
ALTER TABLE hazard_analysis_items ADD COLUMN risk_controls TEXT;
ALTER TABLE hazard_analysis_items ADD COLUMN residual_occurrence INTEGER;
ALTER TABLE hazard_analysis_items ADD COLUMN risk_acceptability_decision VARCHAR(100);
ALTER TABLE hazard_analysis_items ADD COLUMN risk_acceptability_justification TEXT;
ALTER TABLE hazard_analysis_items ADD COLUMN capa_reference TEXT;
ALTER TABLE hazard_analysis_items ADD COLUMN approver_role VARCHAR(255);
ALTER TABLE hazard_analysis_items ADD COLUMN approval_meaning TEXT;
ALTER TABLE hazard_analysis_items ADD COLUMN version_lock BOOLEAN DEFAULT 0;
ALTER TABLE hazard_analysis_items ADD COLUMN review_date DATETIME;
ALTER TABLE hazard_analysis_items ADD COLUMN review_frequency VARCHAR(255);
ALTER TABLE hazard_analysis_items ADD COLUMN last_reviewed_by VARCHAR(255);
ALTER TABLE hazard_analysis_items ADD COLUMN post_market_trigger BOOLEAN DEFAULT 0;
ALTER TABLE hazard_analysis_items ADD COLUMN benefit_risk_analysis_required BOOLEAN DEFAULT 0;
ALTER TABLE hazard_analysis_items ADD COLUMN benefit_risk_justification TEXT;

CREATE INDEX IF NOT EXISTS ix_hazard_analysis_items_last_reviewed_by ON hazard_analysis_items(last_reviewed_by);
