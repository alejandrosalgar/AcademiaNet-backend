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


class PathParams(BaseModel):
    cognito_user_id: str = Field(description="User unique identifier.")


class UserUpdateBody(BaseModel):
    first_name: str = Field(description="User first name.")
    last_name: str = Field(description="User last name.")
    time_zone: Optional[str] = Field(description="User time zone.")
    is_active: Optional[bool] = Field(default=True)


class UserPutSuccessResponse(SuccessResponse):
    cognito_user_id: str = Field(description="User unique identifier.")


DATA_CONTRACT = DataContract(
    request=Request(path_params=PathParams, body=UserUpdateBody),
    responses=[
        Response(
            status_code=HTTPStatus.CREATED,
            description="User updated successfully.",
            body=UserPutSuccessResponse,
        ),
        Response(
            status_code=HTTPStatus.BAD_REQUEST,
            description="Error during user creation process.",
            body=ErrorResponse,
        ),
    ],
)
