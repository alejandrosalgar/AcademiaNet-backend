import base64
import json
import sys
import traceback
from datetime import datetime

from core_utils.boto3.constants import (
    APPKEY_SECRET_ARN,
    CORALOGIX_KEY,
    LAMBDA_CLIENT,
    REGION_NAME,
    RESOURCE_METHOD,
    SECRETS_MANAGER_CLIENT,
    SERVICE_NAME,
    set_database_globals,
)
from core_utils.boto3.secrets_manager import get_secret
from core_utils.constants import CURRENT_DATETIME, HEADERS, UUID, user_agent_handler
from core_utils.exceptions.lambda_exceptions import HttpLambdaException
from core_utils.logging import send_to_coralogix
from core_utils.models.tenant_keys import TenantKeys
from core_utils.models.tenants import Tenants
from core_utils.models.users import UserNotFoundException, Users


def decode_key(key):
    # This function extracts the tenant_id from the Tenant Key
    encoded_bytes = bytes(key, "utf-8")
    decoded_str = str(base64.b64decode(encoded_bytes.decode("utf-8")), "utf-8")
    tenant_id_from_key = decoded_str.split(":")[0]
    return tenant_id_from_key


def check_api_keys(event):
    # This function determines the user_id and tenant_id according to the api key used
    user_agent_handler("User")
    if event["requestContext"]["authorizer"]["claims"]["scope"] == "aws.cognito.signin.user.admin":
        cognito_user_id = event["requestContext"]["authorizer"]["claims"]["username"]
        user = Users(cognito_user_id=cognito_user_id)
        tenant_id = user.get_by_id().get("tenant_id")
        return (cognito_user_id, tenant_id)
    elif event["requestContext"]["authorizer"]["claims"]["scope"] == "apiauthidentifier/json.read":
        if "Tenant-Key" in event["headers"].keys():
            user_agent_handler("Tenant Key")
            tenant_key_value = event["headers"]["Tenant-Key"]
            tenant_id = decode_key(tenant_key_value)
            tenant_key = TenantKeys(tenant_id=tenant_id)
            # Get vault names
            tenant_keys = tenant_key.get_by_tenant_id()
            # Compare key with secrets
            for tenant_key in tenant_keys:
                curr_secret = get_secret(tenant_key.get("secret_name"), REGION_NAME, "Key")
                if curr_secret == tenant_key_value:
                    try:
                        user = Users(
                            tenant_id=tenant_id,
                            first_name=tenant_key.get("secret_name"),
                            last_name="Key",
                        ).get_by_name()
                        cognito_user_id = user.get("cognito_user_id")
                    except UserNotFoundException:
                        user = Users(
                            tenant_id=tenant_id,
                            first_name="Tenant",
                            last_name="Key",
                        ).get_by_name()
                        cognito_user_id = user.get("cognito_user_id")
                    return (cognito_user_id, tenant_id)
            raise Exception("api_keys.InvalidTenantKey")
        elif "App-Key" in event["headers"].keys():
            user_agent_handler("Application Key")
            tenant_id = event["headers"]["tenant_id"]
            app_key = event["headers"]["App-Key"]
            user = Users(
                tenant_id=tenant_id,
                first_name="App",
                last_name="Key",
            ).get_by_name()
            cognito_user_id = user.get("cognito_user_id")
            # Compare key with secrets
            secret_response = SECRETS_MANAGER_CLIENT.get_secret_value(SecretId=APPKEY_SECRET_ARN)
            secret_key = secret_response["SecretString"]
            if secret_key == app_key:
                return (cognito_user_id, tenant_id)
            else:
                raise Exception("api_keys.InvalidApplicationKey")
        else:
            raise Exception("api_keys.ApiKeyNotFoundInHeaders")
    else:
        raise Exception("api_keys.ScopeNotSupported")


def tenant_setup(fn):
    def wrapper(*args, **kwargs):
        # Get tenant_id
        tenant_id = None
        event = args[0]
        set_database_globals()
        if (
            event["requestContext"]["authorizer"]["claims"]["scope"]
            == "aws.cognito.signin.user.admin"
        ):
            cognito_user_id = event["requestContext"]["authorizer"]["claims"]["username"]
            user = Users(cognito_user_id=cognito_user_id)
            tenant_id = user.get_by_id().get("tenant_id")
        elif (
            event["requestContext"]["authorizer"]["claims"]["scope"]
            == "apiauthidentifier/json.read"
        ):
            if "Tenant-Key" in event["headers"].keys():
                tenant_key = event["headers"]["Tenant-Key"]
                tenant_id = decode_key(tenant_key)
            elif "App-Key" in event["headers"].keys():
                tenant_id = event["headers"]["tenant_id"]
            else:
                raise Exception("tenant_configuration.InvalidApplicationKey")
        else:
            raise Exception("tenant_configuration.ScopeNotSupported")
        tenant = Tenants(tenant_id=tenant_id).get_by_id()
        database, resource_arn, secret_arn = (
            tenant.get("database"),
            tenant.get("db_cluster_arn"),
            tenant.get("db_credentials_secrets_store_arn"),
        )
        # Set DB credentials for specific tenant_id
        set_database_globals(database, resource_arn, secret_arn)

        event["user_id"], event["tenant_id"] = check_api_keys(event)
        response = fn(*args, **kwargs)

        return response

    return wrapper


def get_lambda_versions_list(lambda_arn):
    versions_list = []
    next_marker = ""
    while True:
        if next_marker == "":
            lambda_response = LAMBDA_CLIENT.list_versions_by_function(FunctionName=lambda_arn)
        else:
            lambda_response = LAMBDA_CLIENT.list_versions_by_function(
                FunctionName=lambda_arn, Marker=next_marker
            )
        versions_list = versions_list + [
            int(curr_version["Version"])
            for curr_version in lambda_response["Versions"]
            if curr_version["Version"] != "$LATEST"
        ]
        if "NextMarker" not in lambda_response:
            break
        else:
            next_marker = lambda_response["NextMarker"]
    versions_list.sort()
    return versions_list


def invoke_requested_version(lambda_arn, event):
    # Check if requested version is valid
    requested_version = int(event["headers"]["version"])
    if not isinstance(requested_version, int):
        raise Exception("api_versioning.VersionMustBeANegativeInteger")
    if requested_version >= 0:
        raise Exception("api_versioning.VersionMustBeANegativeInteger")

    # Retrieve versions list
    requested_version = requested_version - 1
    versions_list = get_lambda_versions_list(lambda_arn)
    if abs(requested_version) > len(versions_list):
        raise Exception("api_versioning.VersionDoesNotExist")
    version_to_execute = versions_list[requested_version]

    # Execute requested version
    event["headers"].pop("version")
    response = LAMBDA_CLIENT.invoke(
        FunctionName=lambda_arn + ":" + str(version_to_execute),
        InvocationType="RequestResponse",
        Payload=json.dumps(event),
    )
    payload = json.loads(response["Payload"].read())
    return payload


def lambda_decorator(fn):
    """
    fn: it can be a lambda function or a webhook_dispatch decorator
    """

    def wrapper(*args, **kwargs):
        try:
            event = args[0]
            context = args[1]
            if "version" in event.get("headers", {}):
                LAMBDA_ARN = context.invoked_function_arn
                response = invoke_requested_version(LAMBDA_ARN, event)
                return response

            send_to_coralogix(
                CORALOGIX_KEY,
                {"correlation_id": UUID, "Event Received": event},
                SERVICE_NAME,
                RESOURCE_METHOD,
                3,
            )

            response = fn(*args, **kwargs)

            if isinstance(response[1], dict):
                response[1]["correlation_id"] = UUID
            EXECUTION_TIME = str(datetime.now() - CURRENT_DATETIME)
            send_to_coralogix(
                CORALOGIX_KEY,
                {"correlation_id": UUID, "Execution time": EXECUTION_TIME, "response": response[1]},
                SERVICE_NAME,
                RESOURCE_METHOD,
                3,
            )
            return {"statusCode": response[0], "body": json.dumps(response[1]), "headers": HEADERS}
        except HttpLambdaException as lambda_exception:
            exception_response = lambda_exception.response
            return exception_response
        except Exception as error:
            exc_type, _, exc_tb = sys.exc_info()
            print(traceback.format_exc())
            ERROR_MSG = f"Execution failed: {repr(error)}. Line: {str(exc_tb.tb_lineno)}."
            EXECUTION_TIME = str(datetime.now() - CURRENT_DATETIME)
            # Send error message and status to coralogix
            send_to_coralogix(
                CORALOGIX_KEY,
                {
                    "correlation_id": UUID,
                    "Status": "Failure",
                    "Execution time": EXECUTION_TIME,
                    "Error message": ERROR_MSG,
                },
                SERVICE_NAME,
                RESOURCE_METHOD,
                5,
            )
            error_response = {
                "statusCode": 500,
                "body": json.dumps(
                    {"message": ERROR_MSG, "code": str(exc_type), "correlation_id": UUID}
                ),
            }
            error_response["headers"] = HEADERS
            return error_response

    return wrapper
