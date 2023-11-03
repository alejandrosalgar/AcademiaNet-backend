from src.services.user_get import perform

from core_utils.http_utils.api_handler import lambda_decorator, tenant_setup
from core_utils.http_utils.api_utils import build_api_gateway_response
from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Modules, Actions, Components, Subcomponents

@tenant_setup
@lambda_decorator
def lambda_handler(event, _):
    cognito_user_id = event["pathParameters"].get("cognito_user_id")

    user_id = event.get("user_id")
    tenant_id = event.get("tenant_id")

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN.value,
        component=Components.USERS.value,
        subcomponent=Subcomponents.GENERAL.value,
        action=Actions.CAN_READ.value,
    )
    authorization.check_permissions()

    user_info = perform(cognito_user_id)
    return build_api_gateway_response(
        200, "Get user successfully", user = user_info.model_dump(mode="json")
        )