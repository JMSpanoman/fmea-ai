-- Migration: Add trace_link.link_type, audit_log_events, and idempotency_requests tables
-- Date: 2024-01-XX
-- Description: Support for SmartQS Connection Contract enforcement and handoff tracking

-- Add link_type column to trace_links (with default for existing rows)
ALTER TABLE trace_links ADD COLUMN link_type VARCHAR(50) DEFAULT 'traces_to';

-- Create audit_log_events table
CREATE TABLE IF NOT EXISTS audit_log_events (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    details_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_audit_log_events_project ON audit_log_events(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_events_user ON audit_log_events(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_events_type ON audit_log_events(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_events_created ON audit_log_events(created_at);

-- Create idempotency_requests table
CREATE TABLE IF NOT EXISTS idempotency_requests (
    id VARCHAR(255) PRIMARY KEY,
    idempotency_key VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    endpoint VARCHAR(500) NOT NULL,
    request_hash VARCHAR(255),
    response_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(idempotency_key, user_id, endpoint)
);

CREATE INDEX IF NOT EXISTS idx_idempotency_key ON idempotency_requests(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_idempotency_lookup ON idempotency_requests(idempotency_key, user_id, endpoint);
CREATE INDEX IF NOT EXISTS idx_idempotency_user ON idempotency_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_idempotency_expires ON idempotency_requests(expires_at);

-- PostgreSQL compatibility: Use JSONB for JSON columns
-- For SQLite, TEXT is used above; PostgreSQL migration would use:
-- details_json JSONB
-- response_json JSONB

