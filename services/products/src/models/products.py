import re
import uuid
from typing import Any, ClassVar

from pydantic import UUID4, Field, field_validator

from core_utils.sql_handler.sql_operator import CustomBaseModel
from core_utils.exceptions.model_exceptions import ModelException


class InvalidProductException(ModelException):
    """Exception thrown when a user name has special characters"""

    def __init__(
        self, code: str = "InvalidProduct", message: str = "Invalid product name."
    ) -> None:
        self.message = message
        super().__init__(message)


class ProductNotFoundException(ModelException):
    """Product not found exception"""

    def __init__(self, code: str = "ProductNotFound", message: str = "Product not found.") -> None:
        self.message = message
        super().__init__(message)


class Products(CustomBaseModel):
    table: ClassVar[str] = "products_master"
    primary_key: ClassVar[str] = "product_id"

    product_id: UUID4 = Field(frozen=True, default_factory=uuid.uuid4)
    product_name: str = Field(default=None, max_length=70)
    price: float = Field(default=None)
    is_active: bool = Field(default=True)
    tenant_id: UUID4 | None = Field(default=None)

    @field_validator("product_name", mode="before")
    @classmethod
    def validate_first(cls, value: Any):
        """Make sure product name doesn't have special characters"""
        str_value = str(value)
        regex = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
        match = re.search(regex, str_value)
        if match:
            raise InvalidProductException(message="Product cannot have special characters")
        return str_value
