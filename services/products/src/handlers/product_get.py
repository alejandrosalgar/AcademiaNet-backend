from src.services.product_get import perform
from core_utils.http_utils.api_handler import lambda_decorator, tenant_setup
from core_utils.http_utils.api_utils import build_api_gateway_response
from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Modules, Actions, Subcomponents
from src.utils import Components


@tenant_setup
@lambda_decorator
def lambda_handler(event, _):
    product_id = event["pathParameters"].get("product_id")

    user_id = event.get("user_id")
    tenant_id = event.get("tenant_id")

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN,
        component=Components.PRODUCTS,
        subcomponent=Subcomponents.GENERAL,
        action=Actions.CAN_READ,
    )
    authorization.check_permissions()

    product_info = perform(product_id)
    return build_api_gateway_response(
        200, "Get product successfully", product=product_info.model_dump(mode="json")
    )
