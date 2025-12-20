-- Migration: Add AI Events Table
-- Date: 2024-01-20
-- Description: Add AI usage logging for audit trail and governance

CREATE TABLE IF NOT EXISTS ai_events (
    id VARCHAR(255) PRIMARY KEY,
    project_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    
    -- Context
    context_type VARCHAR(100) NOT NULL,
    context_id VARCHAR(255),
    
    -- AI details
    prompt_name VARCHAR(100) NOT NULL,
    input_summary TEXT,
    output_json TEXT,
    
    -- Disposition tracking
    disposition VARCHAR(50),
    disposition_notes TEXT,
    disposition_user_id VARCHAR(255),
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    disposed_at DATETIME,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ai_events_project ON ai_events(project_id);
CREATE INDEX IF NOT EXISTS idx_ai_events_user ON ai_events(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_events_context ON ai_events(context_type, context_id);
CREATE INDEX IF NOT EXISTS idx_ai_events_disposition ON ai_events(disposition);
CREATE INDEX IF NOT EXISTS idx_ai_events_created ON ai_events(created_at);

