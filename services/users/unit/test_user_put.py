from uuid import uuid4

import src
from core_utils.auth_utils.permissions import Permission
from core_utils.core_models.users import Users
from core_utils.http_utils.enums import StatusCodes
from core_utils.lambda_utils.models.events import ApiGatewayEvent
from core_utils.lambda_utils.models.responses import ApiGawewayEventResponse
from core_utils.mocks import http_event_mock
from custom_logger import _get_default_logger_configuration
from pytest_mock import MockerFixture
from src.services.user_put import perform
from utils.mocks import LambdaContext, mock_decorator

mock_decorator("lambda_wrapper")

from src.handlers.users_get import lambda_handler  # isort:skip # noqa: E402

_get_default_logger_configuration().register_white_list_fields(["traceback"])


def test_user_post_succed(mocker: MockerFixture):
    event = ApiGatewayEvent(
        http_event_mock(),
    )
    mocker.patch("src.handlers.user_put.check_api_keys", return_value=(None, None))
    mocker.patch("src.handlers.user_put.select_tenant_database", return_value=None)
    mocker.patch.object(Permission, "check_permissions", return_value=lambda: None)
    mocker.patch("src.handlers.user_put.perform", return_value=None)

    result: ApiGawewayEventResponse = lambda_handler(event, LambdaContext())
    assert result.status_code == StatusCodes.OK


def test_users_get_perform_succed(mocker: MockerFixture):
    mocker.patch("src.services.user_put.user_get_perform", return_value=Users())
    mocker.patch("src.services.user_put.update", return_value=None)
    perform("any_id", uuid4().__str__(), {})
    assert src.services.user_put.user_get_perform.call_count == 1
    assert src.services.user_put.update.call_count == 1
