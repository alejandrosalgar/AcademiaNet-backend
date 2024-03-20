from core_utils.mocks import http_event_mock
from src.handlers.user_get import lambda_handler
from dataclasses import dataclass
from custom_logger import _get_default_logger_configuration

USER_ID = "3d9bbff7-decd-4b9d-a687-046b0d660900"
_get_default_logger_configuration().register_white_list_fields(["traceback"])

@dataclass
class LambdaContext():
    aws_request_id: str = "845d59af-036f-48fc-8f1a-26630a7af8e1"

event = http_event_mock(USER_ID, path_parameters={"cognito_user_id": "845d59af-036f-48fc-8f1a-26630a7af8e0"})

def test_user_get():
    result = lambda_handler(event, LambdaContext())
    assert result.get("statusCode") == 200
