-- PostgreSQL deployments only. SQLite uses ensure_user_columns at startup.
ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_started_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR UNIQUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR;
CREATE TABLE IF NOT EXISTS billing_events (id VARCHAR PRIMARY KEY, created_at TIMESTAMPTZ DEFAULT now());
ALTER TABLE users ADD COLUMN IF NOT EXISTS team_owner_id VARCHAR REFERENCES users(id);
CREATE INDEX IF NOT EXISTS ix_users_team_owner_id ON users(team_owner_id);
CREATE TABLE IF NOT EXISTS team_invitations (
    id VARCHAR PRIMARY KEY, owner_id VARCHAR NOT NULL REFERENCES users(id),
    email VARCHAR NOT NULL, token_hash VARCHAR NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL, accepted_at TIMESTAMPTZ, revoked_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS ix_team_invitations_owner_id ON team_invitations(owner_id);
