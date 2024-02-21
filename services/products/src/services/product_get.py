from src.models.products import Products
from src.dam.products import get_details
from core_utils.sql_handler.sql_operator import validate_uuid
from core_utils.exceptions.lambda_exceptions import HttpLambdaException


def perform(product_id: str) -> Products:
    """Function returns product's data

    Args:
        product_id (str): Product identifier

    Raises:
        HttpLambdaExceptions: validation error

    Returns:
        Products: Product data
    """

    if validate_uuid(product_id):
        product: Products = get_details(product_id)
        if not product:
            raise HttpLambdaException(
                400, {"code": "ProductGet.ProductNotFound", "message": "Product not found"}
            )

    else:
        raise HttpLambdaException(
            400,
            {
                "code": "ProductGet.InvalidProductId",
                "message": "product_id value must be a valid uuid4",
            },
        )

    return product
