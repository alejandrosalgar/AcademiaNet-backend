from http import HTTPStatus

from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Actions, Components, Modules, Subcomponents
from core_utils.http_utils.api_handler import select_tenant_database
from core_utils.http_utils.api_utils import check_api_keys
from core_utils.http_utils.enums import StatusCodes
from core_utils.lambda_utils import lambda_wrapper, polymorphic_event
from core_utils.lambda_utils.models import LambdaContext, LambdaEvent, LambdaHandler
from core_utils.lambda_utils.models.events import ApiGatewayEvent
from core_utils.lambda_utils.models.responses import ApiGawewayEventResponse
from custom_logger.enums import LoggingLevels
from pydantic import BaseModel, Field
from src.services.user_get import perform

from utils.documentation.models import ErrorResponse, SuccessResponse
from utils.documentation.utils import docs
from utils.logger.custom_logger import initialize_logging

initialize_logging()


class UserObject(BaseModel):
    cognito_user_id: str = Field(description="User unique identifier.")
    first_name: str = Field(description="User first name.")
    last_name: str = Field(description="User last name.")
    full_name: str = Field(description="User full name.")
    email: str = Field(description="User valid email.")
    time_zone: str | None = Field(description="User time zone.")
    is_active: bool | None = Field(default=True)
    tenant_id: str = Field(description="User tenant identifier.")
    account_id: str | None = Field(description="User account identifier.", default=None)
    is_account_user: bool | None = Field(default=False)
    created_by: str = Field(description="Created by user identifier.")
    created_at: str = Field(description="Creation date timestamp.")
    updated_by: str = Field(description="Last user update identifier.")
    updated_at: str = Field(description="Last updated date timestamp.")


class PathParams(BaseModel):
    cognito_user_id: str = Field(description="User unique identifier.")


class UserSuccessResponse(SuccessResponse):
    user: str = Field(description="User object.")


@docs.get(
    path="/users/{cognito_user_id}",
    summary="Get a User",
    description="Retrieve a specific user by its ID.",
    responses={
        HTTPStatus.OK: {"description": "User retrieved successfully.", "body": UserSuccessResponse},
        HTTPStatus.NOT_FOUND: {"description": "User not found.", "body": ErrorResponse},
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "Internal Code Error.",
            "body": ErrorResponse,
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Error getting requested User.",
            "body": ErrorResponse,
        },
    },
    request={"path_parameters": PathParams},
    tags=["Users"],
)
@polymorphic_event.register
def api_gateway_event_handler(event: ApiGatewayEvent, _: LambdaContext) -> ApiGawewayEventResponse:
    _, tenant_id = check_api_keys(event.raw_event, validate_tenant=False)
    select_tenant_database(tenant_id)

    user_id, tenant_id = check_api_keys(event.raw_event)
    cognito_user_id = event.path_parameters.get("cognito_user_id")

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN,
        component=Components.USERS,
        subcomponent=Subcomponents.GENERAL,
        action=Actions.CAN_READ,
    )
    authorization.check_permissions()

    user_info = perform(cognito_user_id)

    return ApiGawewayEventResponse(
        status_code=StatusCodes.OK,
        body={"result": "Get user successfully", "user": user_info.model_dump(mode="json")},
    )


@lambda_wrapper(transactional=False, event_logging_level=LoggingLevels.INFO)
def lambda_handler(event: LambdaEvent, context: LambdaContext):
    lambda_handler_creator = LambdaHandler(event, context)
    response = lambda_handler_creator.perform(polymorphic_event)
    return response
