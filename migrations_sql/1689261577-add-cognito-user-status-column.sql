ALTER TABLE users_master ADD COLUMN cognito_user_status VARCHAR DEFAULT 'FORCE_CHANGE_PASSWORD';
CREATE INDEX idx_tenant_id ON users_master(tenant_id);