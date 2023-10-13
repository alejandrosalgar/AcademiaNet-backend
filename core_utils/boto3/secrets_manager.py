import json
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from core_utils.boto3.constants import REGION_NAME, SECRETS_MANAGER_CLIENT


class SecretManagerException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def get_secret(vault_name: str = "", region_name: str = REGION_NAME, secret_name: str = "") -> Any:
    """This functions retrieves secrets from AWS Secrets Manager

    Args:
        vault_name (str, optional): Vault secret name. Defaults to "".
        region_name (str, optional): Secret region. Defaults to REGION_NAME.
        secret_name (str, optional): Secret key name. Defaults to "".

    Returns:
        Any: Secret dictionary or value of the dict key
    """
    try:
        secrets_client = (
            SECRETS_MANAGER_CLIENT
            if region_name == REGION_NAME
            else boto3.client(service_name="secretsmanager", region_name=region_name)
        )

        get_secret_value_response = secrets_client.get_secret_value(SecretId=vault_name)
        secrets = json.loads(get_secret_value_response["SecretString"])
        if secret_name:
            return secrets[secret_name]
        else:
            return secrets
    except ClientError as e:
        # TODO: logging
        raise SecretManagerException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise SecretManagerException(
            "GetSecretException",
            f"Error during get secret function excecution: {str(e)}",
        )


def get_env_or_secret_credential(secret_arn: str, key: str) -> str:
    """Keeps the secrets value in cache and return his value

    Args:
        secret_arn (str): Secret ARN
        key (str): Key that we want from secret

    Returns:
        str: Secret key value
    """
    try:
        SECRETS_CACHE = os.getenv("SECRETS_CACHE")
        cache = {}
        if SECRETS_CACHE:
            cache = json.loads(SECRETS_CACHE)
            if secret_arn in cache:
                return cache[secret_arn].get(key)
        new_cache_secret = get_secret(secret_arn, REGION_NAME, None)
        cache[secret_arn] = new_cache_secret
        os.environ["SECRETS_CACHE"] = json.dumps(cache)
        return cache[secret_arn].get(key)
    except ClientError as e:
        # TODO: logging
        raise SecretManagerException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise SecretManagerException(
            "GetEnvironmentSecretCredentialException",
            f"Error during get environment secret function excecution: {str(e)}",
        )


def set_env_or_secret_credential(secret_arn: str, new_value: dict) -> None:
    """Keeps the secrets value in cache and return his value

    Args:
        secret_arn (str): Secret ARN
        key (str): Key that we want from secret
        value (str): Value that we will set from secret
    """
    try:
        SECRETS_CACHE = os.getenv("SECRETS_CACHE")
        cache = {}
        if SECRETS_CACHE:
            cache = json.loads(SECRETS_CACHE)
            if secret_arn in cache:
                cache[secret_arn] = new_value
                os.environ["SECRETS_CACHE"] = json.dumps(cache)
    except Exception as e:
        # TODO: logging
        raise SecretManagerException(
            "SetSecretException",
            f"Error during set secret function excecution: {str(e)}",
        )
