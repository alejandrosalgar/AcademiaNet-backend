CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS MIGRATIONS_MASTER (
        migration_id UUID DEFAULT uuid_generate_v4 (),
        file_path TEXT,
        file_content TEXT DEFAULT NULL,
        created_at timestamp without time zone DEFAULT NOW(),
        PRIMARY KEY (migration_id));

CREATE TABLE IF NOT EXISTS tenants_master (
        tenant_id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, 
        is_active BOOL DEFAULT true, 
        user_pool_id VARCHAR(100) NOT NULL, 
        identity_pool_id VARCHAR(100) NOT NULL, 
        user_pool_client_id VARCHAR(100) NOT NULL, 
        tenant_name VARCHAR(50) NOT NULL, 
        created_by UUID DEFAULT NULL, 
        updated_by UUID DEFAULT NULL, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        UNIQUE (tenant_name)
);

CREATE TABLE IF NOT EXISTS users_master (
        cognito_user_id UUID PRIMARY KEY, 
        is_active BOOL DEFAULT true, 
        is_account_user BOOL DEFAULT false, 
        tenant_id uuid NOT NULL, 
        account_id uuid, 
        first_name VARCHAR(50) NOT NULL, 
        last_name VARCHAR(50) NOT NULL, 
        full_name VARCHAR(100), 
        email VARCHAR(50) NOT NULL, 
        time_zone VARCHAR(40) DEFAULT 'UTC', 
        created_by UUID DEFAULT NULL, 
        updated_by UUID DEFAULT NULL, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        CONSTRAINT fk_tenant_id 
        FOREIGN KEY(tenant_id) 
        REFERENCES tenants_master(tenant_id)
        ); 

ALTER TABLE tenants_master ADD CONSTRAINT fk_created_by FOREIGN KEY (created_by) REFERENCES users_master(cognito_user_id);
ALTER TABLE tenants_master ADD CONSTRAINT fk_updated_by FOREIGN KEY (updated_by) REFERENCES users_master(cognito_user_id);

CREATE TABLE IF NOT EXISTS components_master ( 
        components_id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, 
        is_active BOOL DEFAULT true, 
        module VARCHAR(100) NOT NULL, 
        component VARCHAR(100) NOT NULL, 
        subcomponent VARCHAR(100) NOT NULL, 
        valid_for VARCHAR(30) DEFAULT 'both',
        created_by uuid, 
        updated_by uuid, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        CONSTRAINT fk_created_by FOREIGN KEY(created_by) REFERENCES users_master(cognito_user_id),
        CONSTRAINT fk_updated_by FOREIGN KEY(updated_by) REFERENCES users_master(cognito_user_id),
        UNIQUE (module, component, subcomponent)
        );

CREATE TABLE IF NOT EXISTS tenant_permissions (
        tenant_permission_id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, 
        tenant_id uuid NOT NULL, 
        components_id uuid NOT NULL, 
        created_by uuid, 
        updated_by uuid, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        CONSTRAINT fk_tenant_id 
        FOREIGN KEY(tenant_id) 
        REFERENCES tenants_master(tenant_id), 
        CONSTRAINT fk_components_id 
        FOREIGN KEY(components_id) 
        REFERENCES components_master(components_id), 
        CONSTRAINT fk_created_by FOREIGN KEY(created_by) REFERENCES users_master(cognito_user_id),
        CONSTRAINT fk_updated_by FOREIGN KEY(updated_by) REFERENCES users_master(cognito_user_id)
                                    );

CREATE TABLE IF NOT EXISTS roles_master (
        role_id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, 
        is_active BOOL DEFAULT true, 
        role VARCHAR(50) NOT NULL, 
        tenant_id uuid NOT NULL, 
        type VARCHAR(10) DEFAULT 'other', 
        created_by uuid, 
        updated_by uuid, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        CONSTRAINT fk_tenant_id 
        FOREIGN KEY(tenant_id) 
        REFERENCES tenants_master(tenant_id),
        CONSTRAINT fk_created_by FOREIGN KEY(created_by) REFERENCES users_master(cognito_user_id),
        CONSTRAINT fk_updated_by FOREIGN KEY(updated_by) REFERENCES users_master(cognito_user_id)
        );

CREATE TABLE IF NOT EXISTS role_permissions (
        role_permission_id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, 
        tenant_id uuid NOT NULL, 
        role_id uuid NOT NULL, 
        components_id uuid NOT NULL, 
        can_create BOOL  DEFAULT false, 
        can_read BOOL DEFAULT false, 
        can_update BOOL DEFAULT false, 
        can_delete BOOL DEFAULT false, 
        created_by uuid, 
        updated_by uuid, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        CONSTRAINT fk_tenant_id 
        FOREIGN KEY(tenant_id) 
        REFERENCES tenants_master(tenant_id), 
        CONSTRAINT fk_role_id 
        FOREIGN KEY(role_id) 
        REFERENCES roles_master(role_id), 
        CONSTRAINT fk_components_id 
        FOREIGN KEY(components_id) 
        REFERENCES components_master(components_id),
        CONSTRAINT fk_created_by FOREIGN KEY(created_by) REFERENCES users_master(cognito_user_id),
        CONSTRAINT fk_updated_by FOREIGN KEY(updated_by) REFERENCES users_master(cognito_user_id)
        );

CREATE TABLE IF NOT EXISTS objects_master (
object_id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, 
tenant_id uuid NOT NULL, 
table_name VARCHAR(50) NOT NULL, 
object_limit INT NOT NULL, 
friendly_name_column VARCHAR(50), 
created_by uuid, 
updated_by uuid, 
created_at TIMESTAMP DEFAULT NOW(), 
updated_at TIMESTAMP DEFAULT NULL, 
CONSTRAINT fk_tenant_id 
FOREIGN KEY(tenant_id) 
REFERENCES tenants_master(tenant_id),
CONSTRAINT fk_created_by FOREIGN KEY(created_by) REFERENCES users_master(cognito_user_id),
CONSTRAINT fk_updated_by FOREIGN KEY(updated_by) REFERENCES users_master(cognito_user_id)
);


CREATE TABLE IF NOT EXISTS user_roles (
        user_role_id uuid DEFAULT uuid_generate_v4 () PRIMARY KEY, 
        tenant_id uuid NOT NULL, 
        cognito_user_id uuid NOT NULL, 
        role_id uuid NOT NULL, 
        created_by uuid, 
        updated_by uuid, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        CONSTRAINT fk_tenant_id 
        FOREIGN KEY(tenant_id) 
        REFERENCES tenants_master(tenant_id), 
        CONSTRAINT fk_cognito_user_id 
        FOREIGN KEY(cognito_user_id) 
        REFERENCES users_master(cognito_user_id), 
        CONSTRAINT fk_role_id 
        FOREIGN KEY(role_id) 
        REFERENCES roles_master(role_id),
        CONSTRAINT fk_created_by FOREIGN KEY(created_by) REFERENCES users_master(cognito_user_id),
        CONSTRAINT fk_updated_by FOREIGN KEY(updated_by) REFERENCES users_master(cognito_user_id)
                            );

