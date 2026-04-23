-- PostgreSQL: MAUDE / openFDA adverse event store (optional if you use SQLAlchemy create_all only)
-- Adjust types for your environment; JSONB is recommended for raw_record on Postgres.

CREATE TABLE IF NOT EXISTS maude_adverse_events (
    id VARCHAR NOT NULL PRIMARY KEY,
    source_system VARCHAR(64) NOT NULL DEFAULT 'openfda_maude',
    source_report_key VARCHAR(512) NOT NULL,
    device_sequence INTEGER NOT NULL DEFAULT 0,
    raw_record JSONB NOT NULL,
    normalized_device_name TEXT,
    event_type VARCHAR(512),
    narrative_text TEXT,
    manufacturer TEXT,
    brand_name TEXT,
    generic_name TEXT,
    date_received DATE,
    product_code VARCHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_maude_adverse_event_source_report_device UNIQUE (source_system, source_report_key, device_sequence)
);

CREATE INDEX IF NOT EXISTS ix_maude_adverse_events_date_received ON maude_adverse_events (date_received);
CREATE INDEX IF NOT EXISTS ix_maude_adverse_events_manufacturer ON maude_adverse_events (manufacturer);
CREATE INDEX IF NOT EXISTS ix_maude_adverse_events_normalized_device ON maude_adverse_events (normalized_device_name);
CREATE INDEX IF NOT EXISTS ix_maude_adverse_events_product_code ON maude_adverse_events (product_code);
