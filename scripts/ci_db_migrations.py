import os
from os import listdir
from os.path import isfile, join

from core_utils.boto3.constants import RESOURCE_METHOD, SERVICE_NAME
from core_utils.boto3.rds import (
    begin_transaction,
    commit_transaction,
    rds_execute_statement,
    rollback_transaction,
)
from core_utils.constants import CORALOGIX_KEY, UUID
from core_utils.logging.coralogix import send_to_coralogix
from core_utils.models.tenants import Tenants


def migration_table_exist():
    sql = "SELECT * FROM information_schema.tables WHERE table_name = 'migrations_master';"
    result = rds_execute_statement(sql)
    if len(result) > 0:
        return True
    else:
        return False


def get_module_migration_files_path(module_path):
    files = []
    if os.path.exists(f"{module_path}/migrations_sql/"):
        files = [
            f"{module_path}/migrations_sql/{f}"
            for f in listdir(f"{module_path}/migrations_sql")
            if isfile(join(f"{module_path}/migrations_sql", f))
        ]
    return files


def insert_migration(file_path, file_content, credential):
    file_content = file_content.replace("'", r"\'")
    sql = f"""INSERT INTO migrations_master (file_path, file_content)
     VALUES ('{file_path}', e'{file_content}');"""
    rds_execute_statement(sql, **credential["rds_params"])


def run_sql_migration(file_path, credential):
    fd = open(file_path, "r")
    sqlFile = fd.read()
    fd.close()

    sqlCommands = [sqlFile]
    if "transaction_id" in credential["rds_params"]:
        credential["rds_params"].pop("transaction_id", None)
    transaction_id = begin_transaction(**credential["rds_params"])
    credential["rds_params"]["transaction_id"] = transaction_id
    credential["transaction_params"]["transaction_id"] = transaction_id
    # Execute every command from the input file
    for command in sqlCommands:
        if command != "":
            try:
                rds_execute_statement(sql=command, **credential["rds_params"])
            except Exception as e:
                send_to_coralogix(
                    CORALOGIX_KEY,
                    {
                        "UUID": UUID,
                        "Status": "Failure",
                        "Migration file": file_path,
                        "Error message": str(e),
                    },
                    SERVICE_NAME,
                    RESOURCE_METHOD,
                    5,
                )
                rollback_transaction(**credential["transaction_params"])
                credential["rds_params"]["transaction_id"] = None
                credential["transaction_params"]["transaction_id"] = None
                return True
    insert_migration(file_path, sqlFile, credential)
    commit_transaction(**credential["transaction_params"])
    credential["rds_params"]["transaction_id"] = None
    credential["transaction_params"]["transaction_id"] = None

    return False


def clean_transaction_var():
    if "TRANSACTION_ID" in globals() and globals()["TRANSACTION_ID"] is not None:
        globals()["TRANSACTION_ID"] = None


def record_migration_exits(file_path, credential):
    try:
        commit_transaction()
    except Exception:
        pass
    sql = f"""SELECT migration_id, file_path, created_at FROM migrations_master
     WHERE file_path = '{file_path}';"""
    result = rds_execute_statement(sql=sql, **credential["rds_params"])
    if len(result) > 0:
        return True
    else:
        return False


def create_migration_table():
    sql = """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE TABLE IF NOT EXISTS MIGRATIONS_MASTER (
            migration_id UUID DEFAULT uuid_generate_v4 (),
            file_path TEXT,
            file_content TEXT DEFAULT NULL,
            created_at timestamp without time zone DEFAULT NOW(),
            PRIMARY KEY (migration_id));"""
    rds_execute_statement(sql)


def run_migrations(files, credentials):
    errors = False
    files = sorted(files)
    for credential in credentials:
        for file_path in files:
            if not record_migration_exits(file_path, credential):
                errors = run_sql_migration(file_path, credential)
                clean_transaction_var()
                if errors:
                    return errors
    return errors


def create_migrations_flow():
    print(f"Migration process started, UUID: {UUID}")
    # Run submodules migration (If you add a new submodule please add him to the end of array)
    # submodules = [f"/src/{f}" for f in listdir("src")]
    # submodules.remove("/src/neojumpstart_core_backend")
    # submodules = ["/src/neojumpstart_core_backend"] + submodules + [""]  # Core first, root last
    submodules = [""]

    MIGRATION_TABLE_EXIST = migration_table_exist()
    if not MIGRATION_TABLE_EXIST:
        create_migration_table()
        globals()["MIGRATION_TABLE_EXIST"] = migration_table_exist()

    error = False
    tenants = Tenants()
    try:
        credentials = tenants.get_tenants_db_credentials()
    except Exception:
        credentials = [{"tenant_id": None, "rds_params": {}, "transaction_params": {}}]

    for submodule in submodules:
        files = get_module_migration_files_path(f".{submodule}")
        error = run_migrations(files, credentials)
        if error:
            print(f"Migration '{submodule}' has errors.")
            break

    if not error:
        print("Migration process success.")


if __name__ == "__main__":
    create_migrations_flow()
