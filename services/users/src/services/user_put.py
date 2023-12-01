
from src.dam.users import update
from typing import Any
from core_utils.core_models.users import Users
from src.services.user_get import perform as user_get_perform
import uuid

def perform(
    cognito_user_id:str,
    user_id: str,
    payload: dict[str, Any],
) -> None:
    """Function returns user's profile data

    Args:
        cognito_user_id: User identifier for the user who will be updated
        user_id (str): User identifier for the user who created the new user.
        payload: (dict[str, Any]): Request query parameters

    Raises:
        HttpLambdaExceptions: validation error

    Returns:
        None
    """
    user: Users = user_get_perform(cognito_user_id=cognito_user_id)
    for key, value in payload.items():
        setattr(user, key, value)
    setattr(user, 'updated_by', uuid.UUID(user_id))

    update(user)
    