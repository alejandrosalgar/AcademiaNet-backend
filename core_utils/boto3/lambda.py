import json

from botocore.exceptions import ClientError

from core_utils.boto3.constants import LAMBDA_CLIENT


class LambdaException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def lambda_excecution(
    lambda_name: str, event_object: dict, lambda_service_name: str, invocation_type: str
) -> dict:
    """
    Run lambda function
    """
    try:
        res = LAMBDA_CLIENT.invoke(
            FunctionName=f"{lambda_service_name}-{lambda_name}",
            InvocationType=invocation_type,
            Payload=json.dumps(event_object),
        )
        if invocation_type == "RequestResponse":
            return json.loads(res["Payload"].read().decode("utf-8"))
        else:
            return {}
    except ClientError as e:
        # TODO: logging
        raise LambdaException(e.response["Error"]["Code"], e.response["Error"]["Message"])
    except Exception as e:
        # TODO: logging
        raise LambdaException(
            "LambdaExcecutionException", f"Error during lambda excecution function: {str(e)}"
        )
