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
from src.handlers.data_contracts.user_get import DATA_CONTRACT
from src.services.user_get import perform

from utils.documentation.models import Docs
from utils.documentation.utils import docs
from utils.logger.custom_logger import initialize_logging

initialize_logging()


@docs.get(
    Docs(
        path="/users/{cognito_user_id}",
        summary="Get a User",
        description="Retrieve a specific user by its ID.",
        data_contract=DATA_CONTRACT,
        tags=["Users"],
    )
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
