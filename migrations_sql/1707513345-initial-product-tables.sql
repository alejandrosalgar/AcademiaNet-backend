CREATE TABLE IF NOT EXISTS products_master (
        product_id uuid DEFAULT uuid_generate_v4 (),
        tenant_id uuid NOT NULL, 
        product_name VARCHAR(100),
        price DECIMAL(10,2),
        is_active BOOL DEFAULT true,
        created_by uuid DEFAULT NULL, 
        updated_by uuid DEFAULT NULL, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL,
        CONSTRAINT fk_tenant_id 
        FOREIGN KEY(tenant_id) 
        REFERENCES tenants_master(tenant_id)
        ); 
