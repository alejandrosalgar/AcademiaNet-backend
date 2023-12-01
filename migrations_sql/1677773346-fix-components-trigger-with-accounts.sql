CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE OR REPLACE FUNCTION add_permissions() RETURNS TRIGGER AS 
$BODY$ 
declare 
r record; 
t record; 
BEGIN 
FOR t IN 
SELECT b.tenant_id 
FROM tenants_master b 
LOOP 
FOR r IN 
SELECT DISTINCT a.role_id, a.type 
FROM   roles_master a 
WHERE a.tenant_id = t.tenant_id 
LOOP 
IF r.type ='admin' THEN 
IF NEW.valid_for != 'account' THEN 
INSERT INTO role_permissions(tenant_id, role_id, components_id, can_create, can_read, can_update, can_delete) VALUES(t.tenant_id, r.role_id, NEW.components_id, true, true, true, true); 
ELSE 
INSERT INTO role_permissions(tenant_id, role_id, components_id, can_create, can_read, can_update, can_delete) VALUES(t.tenant_id, r.role_id, NEW.components_id, false, false, false, false); 
END IF; 
ELSIF	r.type = 'default' AND NEW.module = 'user_settings' AND NEW.component = 'users' AND NEW.subcomponent = 'general' THEN 
INSERT INTO role_permissions(tenant_id, role_id, components_id, can_create, can_read, can_update, can_delete) VALUES(t.tenant_id, r.role_id, NEW.components_id, false, true, true, false); 
ELSIF	r.type = 'account' AND NEW.module = 'account' AND NEW.component = 'my_account' AND NEW.subcomponent = 'general' THEN 
INSERT INTO role_permissions(tenant_id, role_id, components_id, can_create, can_read, can_update, can_delete) VALUES(t.tenant_id, r.role_id, NEW.components_id, true, true, true, true); 
ELSE 
INSERT INTO role_permissions(tenant_id, role_id, components_id, can_create, can_read, can_update, can_delete) VALUES(t.tenant_id, r.role_id, NEW.components_id, false, false, false, false); 
END IF; 
END LOOP; 
INSERT INTO tenant_permissions(tenant_id, components_id) VALUES(t.tenant_id, NEW.components_id); 
END LOOP; 
RETURN NEW; 
END; 
$BODY$ 
language plpgsql; 
DROP TRIGGER IF EXISTS new_permissions ON components_master; 
CREATE TRIGGER new_permissions 
AFTER INSERT 
ON components_master 
FOR EACH ROW 
EXECUTE PROCEDURE add_permissions(); 
