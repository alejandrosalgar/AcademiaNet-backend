import re
import uuid
from typing import Any, ClassVar

from core_utils.exceptions.model_exceptions import ModelException
from core_utils.sql_handler.sql_operator import CustomBaseModel
from pydantic import UUID4, Field, field_validator


class InvalidUsernameException(ModelException):
    """Exception thrown when a user name has special characters"""

    def __init__(self, code: str = "InvalidUserName", message: str = "Invalid user name.") -> None:
        self.message = message
        super().__init__(message)


class UserNotFoundException(ModelException):
    """User not found exception"""

    def __init__(self, code: str = "UserNotFound", message: str = "User not found.") -> None:
        self.message = message
        super().__init__(message)


class Users(CustomBaseModel):
    table: ClassVar[str] = "users_master"
    primary_key: ClassVar[str] = "cognito_user_id"

    cognito_user_id: UUID4 = Field(frozen=True, default_factory=uuid.uuid4)
    first_name: str = Field(default=None, max_length=70)
    last_name: str = Field(default=None, max_length=70)
    full_name: str = Field(default=None, max_length=140)
    email: str = Field(default=None, max_length=100)
    time_zone: str = Field(default=None, max_length=20)
    is_active: bool = Field(default=True)
    is_account_user: bool = Field(default=False)
    tenant_id: UUID4 | None = Field(default=None)
    account_id: UUID4 | None = Field(default=None)

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
