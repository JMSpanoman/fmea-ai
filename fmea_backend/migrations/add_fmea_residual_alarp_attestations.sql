-- Residual ALARP feasibility attestations (residual acceptability workflow).

ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS residual_all_feasible_controls_implemented BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fmea_rows ADD COLUMN IF NOT EXISTS residual_further_reduction_not_practicable BOOLEAN NOT NULL DEFAULT FALSE;
