import json

from botocore.exceptions import ClientError

from core_utils.boto3.constants import SNS_CLIENT


class SNSException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def send_sns_message(message: dict, sns_arn: str):
    try:
        sns_message = {"default": json.dumps(message)}
        response = SNS_CLIENT.publish(
            TargetArn=sns_arn, Message=json.dumps(sns_message), MessageStructure="json"
        )
        # TODO: logging
        return response
    except ClientError as e:
        # TODO: logging
        raise SNSException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise SNSException(
            "SendSNSMessageException",
            f"Error during send sns message function excecution: {str(e)}",
        )
