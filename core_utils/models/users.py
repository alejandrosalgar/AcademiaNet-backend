import re
from typing import Any, ClassVar

from pydantic import Field, field_validator

from core_utils.sql_handler.sql_builder import CustomBaseModel, SQLOperator


class InvalidUsernameException(Exception):
    """Exception thrown when a user name has special characters"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class UserNotFoundException(Exception):
    """User not found exception"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class Users(CustomBaseModel):
    table: ClassVar[str] = "users_master"
    primary_key: ClassVar[str] = "cognito_user_id"

    cognito_user_id: str = Field(frozen=True, max_length=100)
    first_name: str = Field(max_length=70)
    last_name: str = Field(max_length=70)
    full_name: str = Field(max_length=140)
    email: str = Field(max_length=100)
    time_zone: str = Field(max_length=20)
    is_active: bool = Field(default=True)
    is_account_user: bool = Field(default=True)
    tenant_id: str = Field(frozen=True, max_length=100)
    account_id: str = Field(frozen=True, max_length=100)

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_first(cls, value: Any):
        """Make sure user name doesn't have special characters"""
        str_value = str(value)
        regex = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
        match = re.search(regex, str_value)
        if match:
            raise InvalidUsernameException(message="User name cannot have special characters")
        return str_value

    def get_by_name(self) -> "Users":
        filter_obj = self.dict(include={"first_name", "last_name", "tenant_id"})
        user = SQLOperator.select_model(self, **filter_obj)
        if not user:
            raise UserNotFoundException(
                message=(
                    f"User with name {self.first_name} {self.last_name} "
                    f"from {self.tenant_id} tenant not found"
                )
            )
        return user[0]

    def get_by_id(self) -> str:
        filter_obj = self.dict(include={"cognito_user_id"})
        user = SQLOperator.select_model(self, **filter_obj)
        if not user:
            raise UserNotFoundException(message=(f"User with id {self.cognito_user_id} "))
        return user[0]
