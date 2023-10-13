import json

from core_utils.constants import HEADERS, UUID


class HttpLambdaException(Exception):
    def __init__(self, status: int, body: dict = {}) -> None:
        self.response = self._handle_exception(status, body)

    def _handle_exception(self, status, body):
        body["correlation_id"] = UUID
        return {"statusCode": status, "body": json.dumps(body), "headers": HEADERS}


# TODO: SQSLambdaException, EventBridgeLambdaException, SNSLambdaException...
