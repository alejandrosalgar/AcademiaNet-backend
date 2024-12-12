from http import HTTPStatus

from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Actions, Components, Modules, Subcomponents
from core_utils.http_utils.api_handler import select_tenant_database
from core_utils.http_utils.api_utils import check_api_keys
from core_utils.http_utils.enums import StatusCodes
from core_utils.lambda_utils import lambda_wrapper, polymorphic_event
from core_utils.lambda_utils.models import LambdaContext, LambdaHandler
from core_utils.lambda_utils.models.events import ApiGatewayEvent
from core_utils.lambda_utils.models.responses import ApiGawewayEventResponse
from custom_logger.enums import LoggingLevels
from pydantic import BaseModel, Field
from src.services.user_put import perform

from utils.documentation.models import ErrorResponse, SuccessResponse
from utils.documentation.utils import docs
from utils.logger.custom_logger import initialize_logging

initialize_logging()


class PathParams(BaseModel):
    cognito_user_id: str = Field(description="User unique identifier.")


class UserUpdateBody(BaseModel):
    first_name: str = Field(description="User first name.")
    last_name: str = Field(description="User last name.")
    time_zone: str | None = Field(description="User time zone.")
    is_active: bool | None = Field(default=True)


class UserSuccessResponse(SuccessResponse):
    cognito_user_id: str = Field(description="User unique identifier.")


@docs.put(
    path="/users/{cognito_user_id}",
    summary="Update a User",
    description="Update a user for give cognito user identifier.",
    responses={
        HTTPStatus.OK: {"description": "User updated successfully.", "body": UserSuccessResponse},
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "Internal Code Error.",
            "body": ErrorResponse,
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Error during user update process.",
            "body": ErrorResponse,
        },
    },
    request={"body": UserUpdateBody},
    tags=["Users"],
)
@polymorphic_event.register
def api_gateway_event_handler(event: ApiGatewayEvent, _: LambdaContext) -> ApiGawewayEventResponse:
    _, tenant_id = check_api_keys(event.raw_event, validate_tenant=False)
    select_tenant_database(tenant_id)

    user_id, tenant_id = check_api_keys(event.raw_event)
    cognito_user_id = event.path_parameters.get("cognito_user_id")

    payload = event.body

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN,
        component=Components.USERS,
        subcomponent=Subcomponents.GENERAL,
        action=Actions.CAN_UPDATE,
    )
    authorization.check_permissions()

    perform(user_id, tenant_id, payload)

    return ApiGawewayEventResponse(
        status_code=StatusCodes.OK,
        body={"result": "User updated successfully", "cognito_user_id": cognito_user_id},
    )


@lambda_wrapper(transactional=True, event_logging_level=LoggingLevels.INFO)
def lambda_handler(event, context):
    lambda_handler_creator = LambdaHandler(event, context)
    response = lambda_handler_creator.perform(polymorphic_event)
    return response
