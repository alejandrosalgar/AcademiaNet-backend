UPDATE users_master SET updated_at = created_at WHERE updated_at is Null;
UPDATE users_master SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE users_master ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE tenants_master SET updated_at = created_at WHERE updated_at is Null;
UPDATE tenants_master SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE tenants_master ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE components_master SET updated_at = created_at WHERE updated_at is Null;
UPDATE components_master SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE components_master ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE tenant_permissions SET updated_at = created_at WHERE updated_at is Null;
UPDATE tenant_permissions SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE tenant_permissions ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE roles_master SET updated_at = created_at WHERE updated_at is Null;
UPDATE roles_master SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE roles_master ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE role_permissions SET updated_at = created_at WHERE updated_at is Null;
UPDATE role_permissions SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE role_permissions ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE objects_master SET updated_at = created_at WHERE updated_at is Null;
UPDATE objects_master SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE objects_master ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE user_roles SET updated_at = created_at WHERE updated_at is Null;
UPDATE user_roles SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE user_roles ALTER COLUMN updated_at SET DEFAULT NOW();

UPDATE tenant_keys SET updated_at = created_at WHERE updated_at is Null;
UPDATE tenant_keys SET updated_by = created_by WHERE updated_by is Null;
ALTER TABLE tenant_keys ALTER COLUMN updated_at SET DEFAULT NOW();
