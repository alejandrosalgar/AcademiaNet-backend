from http import HTTPStatus
from typing import List

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
from src.services.users_get import GetQueryParams, perform

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


class UserSuccessResponse(SuccessResponse):
    users: List[str] = Field(description="Result users list.")


class QueryParams(BaseModel):
    cognito_user_id: str | None = Field(description="User unique identifier.")
    email: str | None = Field(description="User email filter.")
    full_name: str | None = Field(description="User like name.")
    account_id: str | None = Field(description="Users account identifier.")
    is_active: bool | None = Field(description="Are users active.", default=True)
    page: int | None = Field(description="Page number result.")
    per_page: int | None = Field(description="Page results limit.")


@docs.post(
    path="/users",
    summary="Create a User",
    description="Create a cognito user.",
    responses={
        HTTPStatus.CREATED: {
            "description": "User created successfully.",
            "body": UserSuccessResponse,
        },
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "description": "Internal Code Error.",
            "body": ErrorResponse,
        },
        HTTPStatus.BAD_REQUEST: {
            "description": "Error during user creation process.",
            "body": ErrorResponse,
        },
    },
    request={"query_params": QueryParams},
    tags=["Users"],
)
@polymorphic_event.register
def api_gateway_event_handler(event: ApiGatewayEvent, _: LambdaContext) -> ApiGawewayEventResponse:
    _, tenant_id = check_api_keys(event.raw_event, validate_tenant=False)
    select_tenant_database(tenant_id)

    user_id, tenant_id = check_api_keys(event.raw_event)
    query_params = event.query_string_parameters
    query_params = GetQueryParams(**query_params)

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN,
        component=Components.USERS,
        subcomponent=Subcomponents.GENERAL,
        action=Actions.CAN_UPDATE,
    )
    authorization.check_permissions()

    users_info = perform(tenant_id, query_params)

    return ApiGawewayEventResponse(
        status_code=StatusCodes.OK,
        body={"result": "Get users successfully", "users": users_info},
    )


@lambda_wrapper(transactional=True, event_logging_level=LoggingLevels.INFO)
def lambda_handler(event, context):
    lambda_handler_creator = LambdaHandler(event, context)
    response = lambda_handler_creator.perform(polymorphic_event)
    return response
