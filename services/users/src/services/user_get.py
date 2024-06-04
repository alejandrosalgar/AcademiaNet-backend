from core_utils.core_models.users import Users
from core_utils.http_utils.enums import StatusCodes
from core_utils.lambda_utils.models.exceptions import ApiGatewayEventException
from core_utils.sql_handler.sql_operator import validate_uuid
from src.dam.users import get_details


def perform(cognito_user_id: str) -> Users:
    """Function returns user's profile data

    Args:
        cognito_user_id (str): User identifier

    Raises:
        ApiGatewayEventException: validation error

    Returns:
        Users: User data
    """
    if validate_uuid(cognito_user_id):
        user: Users = get_details(cognito_user_id)
        if not user:
            raise ApiGatewayEventException(
                StatusCodes.NOT_FOUND, code="UserGet.UserNotFound", message="User not found"
            )

    else:
        raise ApiGatewayEventException(
            StatusCodes.BAD_REQUEST,
            code="UserGet.InvalidCognitoUserId",
            message="cognito_user_id value must be a valid uuid4",
        )

    return user
