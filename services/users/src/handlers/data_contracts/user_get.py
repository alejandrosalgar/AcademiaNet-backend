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


class UserGetObject(BaseModel):
    cognito_user_id: str = Field(description="User unique identifier.")
    first_name: str = Field(description="User first name.")
    last_name: str = Field(description="User last name.")
    full_name: str = Field(description="User full name.")
    email: str = Field(description="User valid email.")
    time_zone: Optional[str] = Field(
        description="User time zone.", examples=["UTC", "Bogota/America"]
    )
    is_active: Optional[bool] = Field(default=True)
    tenant_id: str = Field(description="User tenant identifier.")
    account_id: Optional[str] = Field(description="User account identifier.", default=None)
    is_account_user: Optional[bool] = Field(default=False)
    created_by: str = Field(description="Created by user identifier.")
    created_at: str = Field(description="Creation date timestamp.")
    updated_by: str = Field(description="Last user update identifier.")
    updated_at: str = Field(description="Last updated date timestamp.")


class GetUsersSuccessResponse(SuccessResponse):
    user: UserGetObject = Field(description="User object.")


class PathParams(BaseModel):
    cognito_user_id: str = Field(description="User unique identifier.")


DATA_CONTRACT = DataContract(
    request=Request(path_params=PathParams),
    responses=[
        Response(
            status_code=HTTPStatus.OK,
            description="User retrieved successfully.",
            body=GetUsersSuccessResponse,
        ),
        Response(
            status_code=HTTPStatus.NOT_FOUND, description="User not found.", body=ErrorResponse
        ),
        Response(
            status_code=HTTPStatus.BAD_REQUEST,
            description="Error during user retrieval process.",
            body=ErrorResponse,
        ),
    ],
)
