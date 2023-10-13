import json

from botocore.exceptions import ClientError

from core_utils.boto3.constants import REGION_NAME, SQS_CLIENT
from core_utils.boto3.sts import get_external_session


class SQSException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def send_to_queue(event_object: dict, SQS_URL: str):
    try:
        SQS_CLIENT.send_message(
            QueueUrl=SQS_URL, MessageBody=json.dumps(event_object), DelaySeconds=1
        )
    except ClientError as e:
        # TODO: logging
        raise SQSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise SQSException(
            "SendSQSMessageException",
            f"Error during send sqs message function excecution: {str(e)}",
        )


def send_to_external_queue(
    event_object: str,
    sqs_url: str,
    role_arn: str,
    role_session_name: str,
    region: str = REGION_NAME,
) -> None:
    """Sends an SQS event to a AWS Queue from another AWS
    Account.

    Args:
        event_object (str): The string serialized event
        SQS_URL (str): The SQS url to send the event
        role_arn (str): The string value of the ROLE that gives
            permission to access the SQS_URL accross AWS accounts
        rolse_session_name: A name for the AWS session
        region (str): The AWS region
    """
    try:
        session = get_external_session(role_arn, role_session_name)
        QUEUE_CLIENT = session.client("sqs", region)
        QUEUE_CLIENT.send_message(QueueUrl=sqs_url, MessageBody=event_object, DelaySeconds=1)
    except ClientError as e:
        # TODO: logging
        raise SQSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise SQSException(
            "SendSQSMessageExternalAccountException",
            f"Error during send sqs message to external account function excecution: {str(e)}",
        )
