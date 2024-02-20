from pydantic import BaseModel, Field, field_validator

from core_utils.exceptions.lambda_exceptions import QueryParamsMissingError
from src.models.products import Products
from src.dam.products import get_list
from pydantic import UUID4

BOOL_VALUES = {
    "true": True,
    "false": False,
}


class GetQueryParams(BaseModel):
    """Model to define the query parameters"""

    product_id: UUID4 = Field(default=None)
    product_name: str = Field(default=None)
    price: float = Field(default=None)
    is_active: bool = Field(default=None)
    page: int = Field(default=0)
    per_page: int = Field(default=10)

    @field_validator("product_name", mode="before")
    @classmethod
    def to_lowercase(cls, value: str) -> str:
        return f"%{value.lower()}%"

    @field_validator("is_active", mode="before")
    @classmethod
    def to_bool(cls, value: str) -> bool:
        if value:
            if value in BOOL_VALUES:
                return BOOL_VALUES[value]
            raise QueryParamsMissingError(
                message=(
                    "You should provide true or false value "
                    "for is_active query string parameter."
                )
            )
        return value


def perform(tenant_id: str, query_params: GetQueryParams | None = None) -> list[Products]:
    """Function returns product's profile data

    Args:
        tenant_id (str): User's tenant ID
        query_params: (GetQueryParams | None): Request query parameters

    Raises:
        QueryParamsMissingError: If request query parameters has errors


    Returns:
        list[Products]: Products data
    """
    products: list[Products] = get_list(params=query_params, tenant_id=tenant_id)

    return products
