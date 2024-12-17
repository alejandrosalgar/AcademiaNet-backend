from http import HTTPStatus
from typing import Optional

from pydantic import BaseModel, Field

from utils.documentation.models import (
    DataContract,
    ErrorResponse,
    Request,
    Response,
    SuccessResponse,
)


class UserCreationBody(BaseModel):
    first_name: str = Field(description="User first name.")
    last_name: str = Field(description="User last name.")
    email: str = Field(description="User valid email.")
    time_zone: Optional[str] = Field(description="User time zone.")
    is_active: Optional[bool] = Field(default=True)
    tenant_id: str = Field(description="User tenant identifier.")
    account_id: Optional[str] = Field(description="User account identifier.", default=None)
    is_account_user: Optional[bool] = Field(default=False)


class UserCreationSuccessResponse(SuccessResponse):
    cognito_user_id: str


DATA_CONTRACT = DataContract(
    request=Request(body=UserCreationBody),
    responses=[
        Response(
            status_code=HTTPStatus.CREATED,
            description="User created successfully.",
            body=UserCreationSuccessResponse,
        ),
        Response(
            status_code=HTTPStatus.BAD_REQUEST,
            description="Error during user creation process.",
            body=ErrorResponse,
        ),
    ],
)
