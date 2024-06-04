from uuid import uuid4

import src
from core_utils.auth_utils.permissions import Permission
from core_utils.core_models.users import Users
from core_utils.http_utils.enums import StatusCodes
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

from src.handlers.user_get import lambda_handler  # isort:skip # noqa: E402

_get_default_logger_configuration().register_white_list_fields(["traceback"])


def test_user_get(mocker: MockerFixture):
    event = ApiGatewayEvent(http_event_mock())
    mocker.patch("src.handlers.user_get.check_api_keys", return_value=(None, None))
    mocker.patch("src.handlers.user_get.select_tenant_database", return_value=None)
    mocker.patch.object(Permission, "check_permissions", return_value=lambda: None)
    mocker.patch("src.handlers.user_get.perform", return_value=Users())

    result: ApiGawewayEventResponse = lambda_handler(event, LambdaContext())
    assert result.status_code == StatusCodes.OK


def test_user_get_perform_uuid_except(mocker: MockerFixture):
    mocker.patch("src.services.user_get.validate_uuid", return_value=False)
    with raises(ApiGatewayEventException) as result:
        perform("bad_uuid")
    assert src.services.user_get.validate_uuid.call_count == 1
    assert result.value.status_code == StatusCodes.BAD_REQUEST


def test_user_get_not_found(mocker: MockerFixture):
    mocker.patch("src.services.user_get.get_details", return_value=None)
    with raises(ApiGatewayEventException) as result:
        perform(uuid4().__str__())

    assert src.services.user_get.get_details.call_count == 1
    assert result.value.status_code == StatusCodes.NOT_FOUND


def test_user_get_success(mocker: MockerFixture):
    mocker.patch("src.services.user_get.validate_uuid", return_value=True)
    mocker.patch("src.services.user_get.get_details", return_value=Users())
    user = perform(uuid4().__str__())

    assert src.services.user_get.validate_uuid.call_count == 1
    assert src.services.user_get.get_details.call_count == 1
    assert hasattr(user, "cognito_user_id")
