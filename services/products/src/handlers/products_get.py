from src.services.products_get import GetQueryParams, perform

from core_utils.http_utils.api_handler import lambda_decorator, tenant_setup
from core_utils.http_utils.api_utils import build_api_gateway_response
from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Modules, Actions, Subcomponents
from src.utils import initialize_logging, Components

initialize_logging()


@tenant_setup
@lambda_decorator
def lambda_handler(event, _):

    query_params = event.get("queryStringParameters") or {}
    query_params = GetQueryParams(**query_params)

    tenant_id = event.get("tenant_id")
    user_id = event.get("user_id")

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN,
        component=Components.PRODUCTS,
        subcomponent=Subcomponents.GENERAL,
        action=Actions.CAN_READ,
    )
    authorization.check_permissions()
    products_info = perform(tenant_id, query_params)
    return build_api_gateway_response(200, "Get products successfully", products=products_info)
