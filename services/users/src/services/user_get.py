
from core_utils.core_models.users import Users
from src.dam.users import get_details
from core_utils.sql_handler.sql_operator import validate_uuid
from core_utils.exceptions.lambda_exceptions import HttpLambdaException

def perform(
    cognito_user_id: str
) -> Users:
    """Function returns user's profile data

    Args:
        cognito_user_id (str): User identifier

    Raises:
        HttpLambdaExceptions: validation error

    Returns:
        Users: User data
    """

    if validate_uuid(cognito_user_id):
        user: Users = get_details(cognito_user_id)
        if not user:
            raise HttpLambdaException(
                400, {"code": "UserGet.UserNotFound", 
                  "message": "User not found"}
            )

    else:
        raise HttpLambdaException(
            400, {"code": "UserGet.InvalidCognitoUserId", 
                  "message": "cognito_user_id value must be a valid uuid4"}
        )
    
    return user