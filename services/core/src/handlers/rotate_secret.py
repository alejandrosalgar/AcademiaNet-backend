import os

from core_utils.boto3_utils.constants import (
    RESOURCE_METHOD,
    SERVICE_NAME,
)
from core_utils.constants import UUID
from core_utils.boto3_utils.secrets_manager import SECRETS_MANAGER_CLIENT


def create_rotate_secret(arn, token):
    # Make sure the current secret exists
    SECRETS_MANAGER_CLIENT.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")

    # Now try to get the secret version, if that fails, put a new secret
    try:
        SECRETS_MANAGER_CLIENT.get_secret_value(
            SecretId=arn, VersionId=token, VersionStage="AWSPENDING"
        )
        curr_log = f"createSecret: Successfully retrieved secret for {arn}."
        """         send_to_coralogix(
            CORALOGIX_KEY,
            {"correlation_id": UUID, "response": curr_log},
            SERVICE_NAME,
            RESOURCE_METHOD,
            3,
        ) """
    except SECRETS_MANAGER_CLIENT.exceptions.ResourceNotFoundException:
        # Get exclude characters from environment variable
        exclude_characters = (
            os.environ["EXCLUDE_CHARACTERS"] if "EXCLUDE_CHARACTERS" in os.environ else "/@\"'\\"
        )
        # Generate a random password
        passwd = SECRETS_MANAGER_CLIENT.get_random_password(ExcludeCharacters=exclude_characters)

        # Put the secret
        SECRETS_MANAGER_CLIENT.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=passwd["RandomPassword"],
            VersionStages=["AWSPENDING"],
        )
        curr_log = f"createSecret: Successfully put secret for ARN {arn} and version {token}."
        """         send_to_coralogix(
            CORALOGIX_KEY,
            {"correlation_id": UUID, "response": curr_log},
            SERVICE_NAME,
            RESOURCE_METHOD,
            3,
        ) """


def set_secret(arn, token):
    # This is where the secret should be set in the service
    raise NotImplementedError


def test_secret(arn, token):
    # This is where the secret should be tested against the service
    raise NotImplementedError


def finish_rotate_secret(arn, token):
    # First describe the secret to get the current version
    metadata = SECRETS_MANAGER_CLIENT.describe_secret(SecretId=arn)
    current_version = None
    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            if version == token:
                # The correct version is already marked as current, return
                curr_log = f"finishSecret: Version {version} already marked as AWSCURRENT for {arn}"
                """                 send_to_coralogix(
                    CORALOGIX_KEY,
                    {"correlation_id": UUID, "response": curr_log},
                    SERVICE_NAME,
                    RESOURCE_METHOD,
                    3,
                ) """
                return
            current_version = version
            break

    # Finalize by staging the secret version current
    SECRETS_MANAGER_CLIENT.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
    curr_log = (
        f"finishSecret: Successfully set AWSCURRENT stage to version {token} for secret {arn}."
    )
    """     send_to_coralogix(
        CORALOGIX_KEY,
        {"correlation_id": UUID, "response": curr_log},
        SERVICE_NAME,
        RESOURCE_METHOD,
        3,
    ) """


def lambda_handler(event, context):
    # Get initial values
    arn = event["SecretId"]
    token = event["ClientRequestToken"]
    step = event["Step"]

    # Make sure the version is staged correctly
    metadata = SECRETS_MANAGER_CLIENT.describe_secret(SecretId=arn)
    if not metadata["RotationEnabled"]:
        curr_log = f"Secret {arn} is not enabled for rotation"
        """         send_to_coralogix(
            CORALOGIX_KEY,
            {"correlation_id": UUID, "response": curr_log},
            SERVICE_NAME,
            RESOURCE_METHOD,
            3,
        ) """
        raise ValueError(f"Secret {arn} is not enabled for rotation")
    versions = metadata["VersionIdsToStages"]
    if token not in versions:
        curr_log = f"Secret version {token} has no stage for rotation of secret {arn}."
        """         send_to_coralogix(
            CORALOGIX_KEY,
            {"correlation_id": UUID, "response": curr_log},
            SERVICE_NAME,
            RESOURCE_METHOD,
            3,
        ) """
        raise ValueError(f"Secret version {token} has no stage for rotation of secret {arn}.")
    if "AWSCURRENT" in versions[token]:
        curr_log = f"Secret version {token} already set as AWSCURRENT for secret {arn}."
        """         send_to_coralogix(
            CORALOGIX_KEY,
            {"correlation_id": UUID, "response": curr_log},
            SERVICE_NAME,
            RESOURCE_METHOD,
            3,
        ) """
        return
    elif "AWSPENDING" not in versions[token]:
        curr_log = f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}."
        """         send_to_coralogix(
            CORALOGIX_KEY,
            {"correlation_id": UUID, "response": curr_log},
            SERVICE_NAME,
            RESOURCE_METHOD,
            3,
        ) """
        raise ValueError(
            f"Secret version {token} not set as AWSPENDING for rotation of secret {arn}."
        )

    if step == "createSecret":
        create_rotate_secret(arn, token)

    elif step == "setSecret":
        # set_secret( arn, token)
        pass

    elif step == "testSecret":
        # test_secret( arn, token)
        pass

    elif step == "finishSecret":
        finish_rotate_secret(arn, token)
