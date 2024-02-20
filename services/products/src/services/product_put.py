from src.dam.products import update
from typing import Any
from src.models.products import Products
from src.services.product_get import perform as product_get_perform
import uuid


def perform(
    product_id: str,
    user_id: str,
    payload: dict[str, Any],
) -> None:
    """Function returns product's data

    Args:
        product_id: Product identifier for the product who will be updated
        user_id (str): User identifier for the user who created the new product.
        payload: (dict[str, Any]): Request query parameters

    Raises:
        HttpLambdaExceptions: validation error

    Returns:
        None
    """
    product: Products = product_get_perform(product_id=product_id)
    for key, value in payload.items():
        setattr(product, key, value)
    setattr(product, "updated_by", uuid.UUID(user_id))

    update(product)
