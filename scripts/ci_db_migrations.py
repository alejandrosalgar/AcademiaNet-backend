import os
from os import listdir
from os.path import isfile, join
import sys


def setup_project_path():
    # Get the absolute path of the current script's directory
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Get the absolute path of the project's root directory
    project_root_dir = os.path.abspath(os.path.join(current_script_dir, ".."))

    # Add the project's root directory to the sys.path list
    sys.path.append(project_root_dir)


setup_project_path()

import custom_logger
from core_utils.boto3_utils.constants import REGION_NAME, RESOURCE_METHOD, SERVICE_NAME
from core_utils.constants import UUID
from core_utils.core_models.tenants import Tenants
from custom_logger.logger.utils import LoggingLevels

from utils.logger.custom_logger import initialize_logging
from utils.sql_handler.sql_execution import sql_context

initialize_logging()


def migration_table_exist():
    sql = "SELECT * FROM information_schema.tables WHERE table_name = 'migrations_master';"
    result = sql_context.exec(sql, {})
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
    sql_context.exec(sql, {}, **credential["rds_params"])


def run_sql_migration(file_path, credential):
    fd = open(file_path, "r")
    sqlFile = fd.read()
    fd.close()

    sqlCommands = [sqlFile]
    if "transaction_id" in credential["rds_params"]:
        credential["rds_params"].pop("transaction_id", None)
    transaction_id = sql_context.begin_transaction(**credential["rds_params"])
    credential["rds_params"]["transaction_id"] = transaction_id
    credential["transaction_params"]["transaction_id"] = transaction_id
    # Execute every command from the input file
    for command in sqlCommands:
        if command != "":
            try:
                sql_context.exec(command, {}, **credential["rds_params"])
            except Exception as e:
                custom_logger.log(
                    {
                        str(e),
                    },
                    LoggingLevels.ERROR,
                )

                sql_context.rollback_transaction(**credential["transaction_params"])
                credential["rds_params"]["transaction_id"] = None
                credential["transaction_params"]["transaction_id"] = None
                return True
    insert_migration(file_path, sqlFile, credential)
    sql_context.commit_transaction(**credential["transaction_params"])
    credential["rds_params"]["transaction_id"] = None
    credential["transaction_params"]["transaction_id"] = None

    return False


def clean_transaction_var():
    if "TRANSACTION_ID" in globals() and globals()["TRANSACTION_ID"] is not None:
        globals()["TRANSACTION_ID"] = None


def record_migration_exits(file_path, credential):
    try:
        sql_context.commit_transaction()
    except Exception:
        pass
    sql = f"""SELECT migration_id, file_path, created_at FROM migrations_master
     WHERE file_path = '{file_path}';"""
    result = sql_context.exec(sql, {}, **credential["rds_params"])
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
    sql_context.exec(sql, {})


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
    #submodules = [f"/src/{f}" for f in listdir("src")]
    #submodules.remove("/src/neojumpstart_core_backend")
    #submodules = ["/src/neojumpstart_core_backend"] + submodules + [""]  # Core first, root last
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
