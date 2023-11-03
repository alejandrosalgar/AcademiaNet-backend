import json
import os

from core_utils.boto3_utils.rds import (begin_transaction, commit_transaction, 
                                        rollback_transaction, rds_execute_statement)
from core_utils.constants import UUID
from core_utils.core_models.tenants import Tenants


def initialize_functions():
    global CONFIG_FILES
    # submodules = [f"src/{f}" for f in listdir('src')]
    # submodules.remove('src/neojumpstart_core_backend')
    # submodules_config = [
    #     f"{path}/configuration.json" for path in submodules]
    # submodules_config = [f'src/neojumpstart_core_backend/configuration.json'] + \
    #    submodules_config

    submodules_config = []

    # Project configuration file
    if os.path.exists(f'configuration.json'):
        submodules_config.append(f'configuration.json')

    CONFIG_FILES = submodules_config


def create_components(credential):

    for config_file in CONFIG_FILES:
        file_object = open(config_file)
        data = json.load(file_object)

        components = data["components"]
        components_sql = ""
        execute = False
        for component in components:
            if credential['rds_params'] != {}:
                if component[1] == 'tenants':  # Tenants component skiped for other tenants
                    continue
            sql = f"""SELECT COUNT(*) as count FROM components_master 
            WHERE module='{component[0]}' 
            AND component='{component[1]}' 
            AND subcomponent='{component[2]}'
            """
            count = rds_execute_statement(
                sql=sql, **credential['rds_params'])[0]["count"]
            if not count:
                execute = True
                components_sql += f"""INSERT INTO components_master(module,component,subcomponent,valid_for) 
                VALUES ('{component[0]}','{component[1]}','{component[2]}','{component[3]}'); \n"""

        if execute:
            rds_execute_statement(sql=components_sql, **
                                  credential['rds_params'])


def create_object_limit(credential):

    # Check if events submodule creates event columns
    sql = """SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='objects_master' and column_name='primary_object';"""

    has_columns = rds_execute_statement(sql=sql, **credential['rds_params'])

    for config_file in CONFIG_FILES:
        file_object = open(config_file)
        data = json.load(file_object)

        objects = data["objects"]

        objects_sql = ""
        execute = False

        if len(has_columns) == 0:

            for obj in objects:
                if credential['rds_params'] != {}:
                    if obj[0] == 'tenants_master':  # Tenant master skiped for other tenants
                        continue
                sql = f"""SELECT COUNT(*) as count FROM objects_master 
                WHERE table_name = '{obj[0]}' AND tenant_id = '{credential['tenant_id']}'
                """
                count = rds_execute_statement(
                    sql=sql, **credential['rds_params'])[0]["count"]
                if not count:
                    execute = True
                    objects_sql += f"""INSERT INTO objects_master(tenant_id, table_name,
                    object_limit, friendly_name_column) 
                    VALUES('{credential['tenant_id']}', '{obj[0]}', {obj[1]}, '{obj[2]}'); \n"""

            if execute:
                rds_execute_statement(
                    sql=objects_sql, **credential['rds_params'])
        # Objects master with events
        else:

            for obj in objects:
                if credential['rds_params'] != {}:
                    if obj[0] == 'tenants_master':  # Tenant master skiped for other tenants
                        continue
                sql = f"""SELECT object_id FROM objects_master 
                WHERE table_name = '{obj[0]}' AND tenant_id = '{credential['tenant_id']}'
                """
                object_data = rds_execute_statement(sql=sql, **credential['rds_params'])
                count = len(object_data)

                if obj[5] is not None:
                    parent_object_sql = f"""SELECT object_id FROM objects_master 
                        WHERE table_name = '{obj[5]}' AND tenant_id = '{credential['tenant_id']}'"""
                    parent_object_data = rds_execute_statement(sql=parent_object_sql, 
                                                               **credential['rds_params'])
                    parent_object_id = parent_object_data[0]["object_id"] if len(
                        parent_object_data) else "null"

                else:
                    parent_object_id = "null"

                if parent_object_id != "null":
                    if not count:
                        objects_sql += f"""INSERT INTO objects_master(tenant_id, 
                                    table_name,object_limit, friendly_name_column,
                                    primary_object , linking_table , parent_object) 
                        VALUES('{credential['tenant_id']}', '{obj[0]}', {obj[1]}, '{obj[2]}', 
                        {obj[3]}, {obj[4]}, '{parent_object_id}'); \n"""
                    else:
                        objects_sql += f"""UPDATE objects_master 
                                    SET tenant_id = '{credential['tenant_id']}', 
                                    table_name = '{obj[0]}', object_limit = {obj[1]},
                                    friendly_name_column = '{obj[2]}', primary_object = {obj[3]} , 
                                    linking_table = {obj[4]} , parent_object = '{parent_object_id}' 
                                    WHERE object_id = '{object_data[0]["object_id"]}'; \n"""
                else:
                    if not count:
                        objects_sql += f"""INSERT INTO objects_master(tenant_id, 
                                    table_name,object_limit, friendly_name_column,
                                    primary_object , linking_table , parent_object) 
                        VALUES('{credential['tenant_id']}', '{obj[0]}', {obj[1]}, '{obj[2]}', 
                                {obj[3]}, {obj[4]}, {parent_object_id}); \n"""
                    else:
                        objects_sql += f"""UPDATE objects_master 
                                    SET tenant_id = '{credential['tenant_id']}', 
                                    table_name = '{obj[0]}', object_limit = {obj[1]},
                                    friendly_name_column = '{obj[2]}', primary_object = {obj[3]} , 
                                    linking_table = {obj[4]} , parent_object = {parent_object_id} 
                                    WHERE object_id = '{object_data[0]["object_id"]}'; \n"""
            if len(objects) > 0:
                rds_execute_statement(
                    sql=objects_sql, **credential['rds_params'])


def add_relation_objects_components(credential):

    for config_file in CONFIG_FILES:
        file_object = open(config_file)
        data = json.load(file_object)

        objects = data["objects"]

        for object in objects:
            if credential['rds_params'] != {}:
                if object[0] == 'tenants_master':  # Tenant master skiped for other tenants
                    continue
            if len(object) < 7:
                continue

            if not isinstance(object[6], str):
                continue

            table_name = object[0]
            component_key = object[6]

            sql = f"""
                SELECT components_id FROM components_master
                WHERE CONCAT( module, '.', component, '.', subcomponent) = '{component_key}';
            """
            id_component = rds_execute_statement(sql=sql, **credential['rds_params']
            )[0]['components_id']

            sql = f"""
                UPDATE objects_master SET component_id = '{id_component}'
                WHERE table_name = '{table_name}';
            """
            rds_execute_statement(sql=sql, **credential['rds_params'])


def create_objects_flow():
    initialize_functions()
    print(f"Creation DB objects and permission process started, UUID: {UUID}")
    # Run submodules migration (If you add a new submodule please add him to the end of array)
    try:
        credentials = Tenants.get_tenants_db_credentials()
        for credential in credentials:
            transaction_id = begin_transaction(**credential['rds_params'])
            credential['rds_params']['transaction_id'] = transaction_id
            credential['transaction_params']['transaction_id'] = transaction_id
            create_components(credential)
            create_object_limit(credential)
            add_relation_objects_components(credential)
            commit_transaction(**credential['transaction_params'])
            if 'TRANSACTION_ID' in globals() and globals()['TRANSACTION_ID'] != None:
                globals()['TRANSACTION_ID'] = None
        print("Creation success.")
    except Exception as e:
        rollback_transaction(**credential['transaction_params'])
        print("Creation objects has errors", str(e))

    print("Creation DB objects and permission process finished.")


if __name__ == '__main__':
    create_objects_flow()
