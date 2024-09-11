# flake8: noqa
from core_utils.constants import UserAgent
from core_utils.http_utils.enums import StatusCodes, UserAgents
from core_utils.sql_handler.sql_manager import SqlContext

from utils.sql_handler.pg_client import PGClient

SqlContext.DEFAULT_SQL_MANAGER = PGClient()
UserAgent.DEFAULT_USER_AGENT = UserAgents.APP_KEY_USER

from uuid import uuid4

import src
from core_utils.lambda_utils.models.events import ApiGatewayEvent
from core_utils.lambda_utils.models.exceptions import ApiGatewayEventException
from core_utils.lambda_utils.models.responses import ApiGawewayEventResponse
from core_utils.mocks import http_event_mock
from custom_logger import _get_default_logger_configuration
from pytest import raises
from pytest_mock import MockerFixture
from src.services.user_get import perform

from utils.mocks import LambdaContext, mock_decorator

mock_decorator("lambda_wrapper")
from src.handlers.user_get import lambda_handler

_get_default_logger_configuration().register_white_list_fields(["traceback", "sql"])
USER_ID = "845d59af-036f-48fc-8f1a-26630a7af8e0"


def test_user_get():
    event = ApiGatewayEvent(
        http_event_mock(user_id=USER_ID, path_parameters={"cognito_user_id": USER_ID})
    )

    result: ApiGawewayEventResponse = lambda_handler(event, LambdaContext())
    assert result.status_code == StatusCodes.OK


def test_user_get_perform_uuid_except(mocker: MockerFixture):
    mocker.patch("src.services.user_get.validate_uuid", return_value=False)
    with raises(ApiGatewayEventException) as result:
        perform("bad_uuid")
    assert src.services.user_get.validate_uuid.call_count == 1
    assert result.value.status_code == StatusCodes.BAD_REQUEST


def test_user_get_not_found():
    with raises(ApiGatewayEventException) as result:
        perform(uuid4().__str__())
    assert result.value.status_code == StatusCodes.NOT_FOUND


def test_user_get_success():
    user = perform(USER_ID)

    assert hasattr(user, "cognito_user_id")
