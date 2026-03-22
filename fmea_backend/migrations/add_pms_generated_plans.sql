-- PMS generated plans (Postgres). SQLite uses runtime migration + SQLAlchemy create_all.
CREATE TABLE IF NOT EXISTS pms_generated_plans (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_name VARCHAR(512) NOT NULL,
    intended_use TEXT NOT NULL,
    summary TEXT,
    status VARCHAR(32) NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    payload_json JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_pms_gen_plans_project ON pms_generated_plans (project_id);
CREATE INDEX IF NOT EXISTS ix_pms_gen_plans_created ON pms_generated_plans (created_at);
