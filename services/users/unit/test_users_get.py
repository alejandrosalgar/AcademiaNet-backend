from typing import List

import src
from core_utils.auth_utils.permissions import Permission
from core_utils.exceptions.lambda_exceptions import QueryParamsMissingError
from core_utils.http_utils.enums import StatusCodes
from core_utils.lambda_utils.models.events import ApiGatewayEvent
from core_utils.lambda_utils.models.responses import ApiGawewayEventResponse
from core_utils.mocks import http_event_mock
from custom_logger import _get_default_logger_configuration
from pytest import raises
from pytest_mock import MockerFixture
from src.services.users_get import GetQueryParams, perform
from utils.mocks import LambdaContext, mock_decorator

mock_decorator("lambda_wrapper")

from src.handlers.users_get import lambda_handler  # isort:skip # noqa: E402

_get_default_logger_configuration().register_white_list_fields(["traceback"])


def test_users_get_succed(mocker: MockerFixture):
    event = ApiGatewayEvent(
        http_event_mock(query_parameters={"full_name": "Test User"}),
    )
    mocker.patch("src.handlers.users_get.check_api_keys", return_value=(None, None))
    mocker.patch("src.handlers.users_get.select_tenant_database", return_value=None)
    mocker.patch.object(Permission, "check_permissions", return_value=lambda: None)
    mocker.patch("src.handlers.users_get.perform", return_value=List)

    result: ApiGawewayEventResponse = lambda_handler(event, LambdaContext())
    assert result.status_code == StatusCodes.OK


def test_users_get_perform_succed(mocker: MockerFixture):
    mocker.patch("src.services.users_get.get_list", return_value=[])
    result = perform("any_id")
    assert src.services.users_get.get_list.call_count == 1
    assert isinstance(result, List)


def check_valid_boolean_values():
    with raises(QueryParamsMissingError) as result:
        GetQueryParams(is_active="active")

    assert result.value.code == "UsersGet.BadQueryParams"
