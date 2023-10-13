import boto3
from botocore.exceptions import ClientError

from core_utils.boto3.constants import STS_CLIENT


class STSException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def get_external_session(role_arn: str, role_session_name: str) -> None:
    """Get a session of external aws account
    Account.

    Args:
        role_arn (str): The string value of the ROLE that gives
            permission to access the resurce accross AWS accounts
        rolse_session_name: A name for the AWS session
    """
    try:
        assumed_role_object = STS_CLIENT.assume_role(
            RoleArn=role_arn,
            RoleSessionName=role_session_name,
        )
        credentials = assumed_role_object["Credentials"]
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
        )
        return session
    except ClientError as e:
        # TODO: logging
        raise STSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise STSException(
            "GetSTSSessionException",
            f"Error during get external session function excecution: {str(e)}",
        )
