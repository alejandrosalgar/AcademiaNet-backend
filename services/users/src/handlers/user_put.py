from src.services.user_put import perform
import json
from core_utils.http_utils.api_handler import lambda_decorator, tenant_setup
from core_utils.http_utils.api_utils import build_api_gateway_response
from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Modules, Actions, Components, Subcomponents

@tenant_setup
@lambda_decorator
def lambda_handler(event, _):
    cognito_user_id = event["pathParameters"].get("cognito_user_id")
    payload = json.loads(event["body"])

    user_id = event.get("user_id")
    tenant_id = event.get("tenant_id")

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN.value,
        component=Components.USERS.value,
        subcomponent=Subcomponents.GENERAL.value,
        action=Actions.CAN_UPDATE.value,
    )
    authorization.check_permissions()

    perform(cognito_user_id, user_id, payload)
    return build_api_gateway_response(
        200, "User updated successfully", cognito_user_id = cognito_user_id
        )