CREATE TABLE IF NOT EXISTS TESTING (
        test_id uuid DEFAULT uuid_generate_v4 (),
        name VARCHAR(100) NOT NULL,
        created_by UUID DEFAULT NULL, 
        updated_by UUID DEFAULT NULL, 
        created_at TIMESTAMP DEFAULT NOW(), 
        updated_at TIMESTAMP DEFAULT NULL, 
        PRIMARY KEY (test_id));
