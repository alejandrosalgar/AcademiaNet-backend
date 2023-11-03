import json
import os
import sys

import botocore

from core_utils.boto3_utils.constants import (
    SERVICE_NAME,
    TENANTS_BUCKET,
)
from core_utils.boto3_utils.rds import rds_execute_statement
from core_utils.boto3_utils.cognito import COGNITO_CLIENT
from core_utils.boto3_utils.s3 import S3_RESOURCE
from core_utils.boto3_utils.ses import SES_CLIENT
from core_utils.constants import HEADERS, UUID


def initialize_functions():
    global USER_EMAIL, USER_FIRST_NAME, USER_LAST_NAME, TENANT_NAME
    global USER_POOL_ID, IDENTITY_POOL_ID, USER_POOL_CLIENT_ID
    USER_EMAIL = os.environ["USER_EMAIL"]
    USER_FIRST_NAME = os.environ["USER_FIRST_NAME"]
    USER_LAST_NAME = os.environ["USER_LAST_NAME"]
    TENANT_NAME = os.environ["TENANT_NAME"]
    USER_POOL_ID = os.environ["USER_POOL_ID"]
    IDENTITY_POOL_ID = os.environ["IDENTITY_POOL_ID"]
    USER_POOL_CLIENT_ID = os.environ["USER_POOL_CLIENT_ID"]


def create_email_access_role_policy(email_arn: str) -> dict:
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Principal": {"Service": "cognito-idp.amazonaws.com"},
                "Action": ["ses:SendEmail", "ses:SendRawEmail"],
                "Resource": [email_arn],
                "Effect": "Allow",
            }
        ],
    }


def insert_tenant():
    sql = f"""SELECT COUNT(*) as count FROM tenants_master WHERE tenant_name = '{TENANT_NAME}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_insert_tenant = (
            "INSERT INTO tenants_master "
            "(user_pool_id, identity_pool_id, user_pool_client_id, tenant_name) "
            "VALUES ("
            f"'{USER_POOL_ID}', "
            f"'{IDENTITY_POOL_ID}', "
            f"'{USER_POOL_CLIENT_ID}', "
            f"'{TENANT_NAME}'"
            ")"
        )
        rds_execute_statement(sql_insert_tenant)


def get_tenant_id():
    global TENANT_ID
    sql_tenant_id = f"SELECT tenant_id FROM tenants_master WHERE tenant_name='{TENANT_NAME}'"
    TENANT_ID = rds_execute_statement(sql_tenant_id)[0]["tenant_id"]


def create_default_role():
    global role_id
    sql = f"""SELECT COUNT(*) as count FROM roles_master WHERE role = 'default'
    AND type = 'default' AND  tenant_id = '{TENANT_ID}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_default_role_creation = (
            "INSERT INTO roles_master (role, tenant_id, type)"
            "VALUES("
            f"'default', "
            f"'{TENANT_ID}',"
            f"'default'"
            ")"
        )
        rds_execute_statement(sql_default_role_creation)

    sql = f"""SELECT COUNT(*) as count FROM roles_master WHERE role = 'account'
      AND type = 'other' AND  tenant_id = '{TENANT_ID}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_create_account_role = (
            "INSERT INTO roles_master ( role, tenant_id, type) "
            "VALUES ("
            f"'account', "
            f"'{TENANT_ID}', "
            f"'other'"
            ") RETURNING role_id"
        )
        role_id = rds_execute_statement(sql_create_account_role)[0]["role_id"]
    else:
        sql = f"""SELECT role_id FROM roles_master WHERE role = 'account'
          AND type = 'other' AND  tenant_id = '{TENANT_ID}'"""
        role_id = rds_execute_statement(sql)[0]["role_id"]


def create_user():
    global cognito_user_id

    try:
        cognito_response = COGNITO_CLIENT.admin_get_user(
            UserPoolId=USER_POOL_ID, Username=USER_EMAIL
        )
        cognito_user_id = cognito_response["Username"]

    except COGNITO_CLIENT.exceptions.UserNotFoundException:
        cognito_response = COGNITO_CLIENT.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=USER_EMAIL,
            UserAttributes=[
                {"Name": "email_verified", "Value": "True"},
                {"Name": "email", "Value": USER_EMAIL},
            ],
            DesiredDeliveryMediums=["EMAIL"],
        )
        cognito_user_id = cognito_response["User"]["Username"]

    sql = f"""SELECT COUNT(*) as count FROM users_master WHERE
      cognito_user_id = '{cognito_user_id}' AND tenant_id = '{TENANT_ID}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_insert_user = (
            f"INSERT INTO users_master (cognito_user_id, first_name, last_name, email, tenant_id) "
            "VALUES ("
            f"'{cognito_user_id}', "
            f"'{USER_FIRST_NAME}', "
            f"'{USER_LAST_NAME}', "
            f"'{USER_EMAIL}', "
            f"'{TENANT_ID}'"
            ")"
        )
        rds_execute_statement(sql_insert_user)

    # assignation of the default role
    sql_default_role_id = (
        f"SELECT role_id FROM roles_master WHERE tenant_id='{TENANT_ID}' AND type = 'default'"
    )
    default_role_id = rds_execute_statement(sql_default_role_id)

    for role in default_role_id:
        sql = f"""SELECT COUNT(*) as count FROM user_roles
        WHERE cognito_user_id = '{cognito_user_id}'
          AND role_id = '{role["role_id"]}' AND  tenant_id = '{TENANT_ID}'"""
        count = rds_execute_statement(sql)[0]["count"]
        if not count:
            assign_default_role_query = (
                "INSERT INTO user_roles"
                "(tenant_id, cognito_user_id, role_id) VALUES"
                f"('{TENANT_ID}','{cognito_user_id}','{role['role_id']}');"
            )
            rds_execute_statement(assign_default_role_query)


def assign_role():
    sql = f"""SELECT COUNT(*) as count FROM roles_master WHERE role = 'admin'
      AND type = 'admin' AND  tenant_id = '{TENANT_ID}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_create_role = (
            "INSERT INTO roles_master ( role, tenant_id, type) "
            "VALUES ("
            f"'admin', "
            f"'{TENANT_ID}', "
            f"'admin'"
            ")"
        )
        rds_execute_statement(sql_create_role)

    sql_default_role_id = (
        f"SELECT role_id FROM roles_master WHERE tenant_id='{TENANT_ID}' AND type = 'admin'"
    )
    ROLE_ID = rds_execute_statement(sql_default_role_id)[0]["role_id"]

    sql = f"""SELECT COUNT(*) as count FROM user_roles WHERE cognito_user_id = '{cognito_user_id}'
      AND role_id = '{ROLE_ID}' AND  tenant_id = '{TENANT_ID}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_assign_role = (
            f"INSERT INTO user_roles (tenant_id, cognito_user_id, role_id) "
            "VALUES ("
            f"'{TENANT_ID}', "
            f"'{cognito_user_id}', "
            f"'{ROLE_ID}'"
            ")"
        )
        rds_execute_statement(sql_assign_role)


def create_app_tenant_user():
    # Tenant user
    sql = f"""SELECT COUNT(*) as count FROM users_master WHERE first_name = 'Tenant'
    AND last_name = 'Key'
    AND email = 'Tenant-Key'
    AND tenant_id = '{TENANT_ID}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_insert_user = (
            f"INSERT INTO users_master (cognito_user_id, first_name, last_name, email, tenant_id) "
            "VALUES ("
            f"uuid_generate_v4(), "
            f"'Tenant', "
            f"'Key', "
            f"'Tenant-Key', "
            f"'{TENANT_ID}'"
            ")"
        )
        rds_execute_statement(sql_insert_user)

    # App user
    sql = f"""SELECT COUNT(*) as count FROM users_master WHERE first_name = 'App'
    AND last_name = 'Key'
    AND email = 'App-Key'
    AND tenant_id = '{TENANT_ID}'"""
    count = rds_execute_statement(sql)[0]["count"]
    if not count:
        sql_insert_user = (
            f"INSERT INTO users_master (cognito_user_id, first_name, last_name, email, tenant_id) "
            "VALUES ("
            f"uuid_generate_v4(), "
            f"'App', "
            f"'Key', "
            f"'App-Key', "
            f"'{TENANT_ID}'"
            ")"
        )
        rds_execute_statement(sql_insert_user)


def bucket_file_exist(path):
    try:
        S3_RESOURCE.Object(TENANTS_BUCKET, path).load()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            # Something else has gone wrong.
            raise Exception(f"Error while bucket validation {str(e)}")
    else:
        # The object does exist.
        return True


def create_bucket_file(file_path, key_path):
    try:
        S3_RESOURCE.Bucket(TENANTS_BUCKET).upload_file(file_path, key_path)
    except Exception as e:
        raise Exception(f"Error while bucket file creation {str(e)}")


def create_default_assets():
    USER_CREATION_TEMPLATE_PATH = "./src/email_templates/user_creation.html"
    FORGOT_PASSWORD_TEMPLATE_PATH = "./src/email_templates/forgot_password.html"
    S3_USER_CREATION_TEMPLATE_PATH = "assets_common/email_templates/user_creation.html"
    S3_FORGOT_PASSWORD_TEMPLATE_PATH = "assets_common/email_templates/forgot_password.html"
    if not bucket_file_exist(S3_USER_CREATION_TEMPLATE_PATH):
        create_bucket_file(USER_CREATION_TEMPLATE_PATH, S3_USER_CREATION_TEMPLATE_PATH)
    if not bucket_file_exist(S3_FORGOT_PASSWORD_TEMPLATE_PATH):
        create_bucket_file(FORGOT_PASSWORD_TEMPLATE_PATH, S3_FORGOT_PASSWORD_TEMPLATE_PATH)


def create_cognito_ses_policy() -> None:
    email_arn = os.environ["SES_EMAIL_ARN"]
    email_domain = os.environ["SES_DOMAIN"]
    policy_name = f"{SERVICE_NAME}-cognitoses"
    # Check if the entity exist, else create
    list_identities = SES_CLIENT.list_identities()["Identities"]
    if email_domain not in list_identities:
        if "@" not in email_domain:
            SES_CLIENT.verify_domain_identity(Domain=email_domain)
        else:
            SES_CLIENT.verify_email_identity(EmailAddress=email_domain)

    # Check if the policy already exist, else create
    list_identity_policies = SES_CLIENT.list_identity_policies(Identity=email_arn)["PolicyNames"]
    if policy_name not in list_identity_policies:
        SES_CLIENT.put_identity_policy(
            Identity=email_arn,
            PolicyName=policy_name,
            Policy=json.dumps(create_email_access_role_policy(email_arn)),
        )


def lambda_handler(event, context):
    try:
        initialize_functions()
        insert_tenant()
        get_tenant_id()
        create_default_assets()
        create_default_role()
        create_cognito_ses_policy()
        create_user()
        assign_role()
        create_app_tenant_user()
        return {
            "statusCode": 200,
            "body": "Resources Created",
            "headers": HEADERS,
        }
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        ERROR_MSG = f"Execution failed: {repr(e)}. Line: {str(exc_tb.tb_lineno)}."
        return {
            "statusCode": 500,
            "body": json.dumps(
                {"message": ERROR_MSG, "code": str(exc_type), "correlation_id": UUID}
            ),
            "headers": HEADERS,
        }
