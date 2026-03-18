-- Migration: Add generated_documents table
-- Description: Device-scoped generated documents with versioned content (JSON and markdown)

CREATE TABLE IF NOT EXISTS generated_documents (
    id VARCHAR(255) PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    document_type VARCHAR(128),
    title VARCHAR(512),
    content_json TEXT,
    content_markdown TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_generated_documents_device_id ON generated_documents(device_id);
CREATE INDEX IF NOT EXISTS ix_generated_documents_document_type ON generated_documents(document_type);
