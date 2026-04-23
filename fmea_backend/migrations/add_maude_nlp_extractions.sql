-- PostgreSQL: structured NLP extraction rows for MAUDE narratives (optional if using SQLAlchemy create_all)

CREATE TABLE IF NOT EXISTS maude_nlp_extractions (
    id VARCHAR NOT NULL PRIMARY KEY,
    maude_event_id VARCHAR NOT NULL REFERENCES maude_adverse_events(id) ON DELETE CASCADE,
    failure_mode TEXT,
    cause TEXT,
    effect TEXT,
    component TEXT,
    harm TEXT,
    outcome_classification VARCHAR(32),
    confidence_score DOUBLE PRECISION,
    normalized_risk_phrase TEXT,
    llm_model VARCHAR(128),
    raw_llm_response JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    CONSTRAINT uq_maude_nlp_extraction_event UNIQUE (maude_event_id)
);

CREATE INDEX IF NOT EXISTS ix_maude_nlp_outcome ON maude_nlp_extractions (outcome_classification);
CREATE INDEX IF NOT EXISTS ix_maude_nlp_normalized_phrase ON maude_nlp_extractions (normalized_risk_phrase);
