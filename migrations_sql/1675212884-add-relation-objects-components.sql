ALTER TABLE objects_master ADD COLUMN component_id uuid;
ALTER TABLE objects_master ADD CONSTRAINT fk_component_id FOREIGN KEY ( component_id) REFERENCES components_master(components_id);