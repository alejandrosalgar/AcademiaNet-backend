ALTER TABLE tenants_master
    ADD COLUMN subdomain VARCHAR NULL,
    ADD COLUMN tenant_bucket VARCHAR NULL;