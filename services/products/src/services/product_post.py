from src.dam.products import insert
from typing import Any


def perform(
    user_id: str,
    tenant_id: str,
    payload: dict[str, Any],
) -> str:
    """Function returns product's profile data

    Args:
        user_id (str): User identifier for the user who created the new product.
        tenant_id (str): User's tenant ID
        payload: (dict[str, Any]): Request query parameters

    Raises:
        InsertionError: Bad parameters in payload

    Returns:
        str: cognito user identifier
    """

    product_id = insert(user_id, tenant_id, payload)

    return product_id
