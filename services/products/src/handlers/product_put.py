import json
from core_utils.http_utils.api_handler import lambda_decorator, tenant_setup
from core_utils.http_utils.api_utils import build_api_gateway_response
from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Modules, Actions, Subcomponents
from src.utils import Components
from src.services.product_put import perform


@tenant_setup
@lambda_decorator
def lambda_handler(event, _):
    product_id = event["pathParameters"].get("product_id")
    payload = json.loads(event["body"])

    user_id = event.get("user_id")
    tenant_id = event.get("tenant_id")

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN,
        component=Components.PRODUCTS,
        subcomponent=Subcomponents.GENERAL,
        action=Actions.CAN_UPDATE,
    )
    authorization.check_permissions()

    perform(product_id, user_id, payload)
    return build_api_gateway_response(
        200, "Product updated successfully", product_id=product_id
    )
