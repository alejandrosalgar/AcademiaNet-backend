from http import HTTPStatus
from typing import List, Optional

from pydantic import BaseModel, Field

from utils.documentation.models import (
    DataContract,
    ErrorResponse,
    Request,
    Response,
    SuccessResponse,
)


class UserObject(BaseModel):
    cognito_user_id: str = Field(description="User unique identifier.")
    first_name: str = Field(description="User first name.")
    last_name: str = Field(description="User last name.")
    full_name: str = Field(description="User full name.")
    email: str = Field(description="User valid email.")
    time_zone: Optional[str] = Field(description="User time zone.")
    is_active: Optional[bool] = Field(default=True)
    tenant_id: str = Field(description="User tenant identifier.")
    account_id: Optional[str] = Field(description="User account identifier.", default=None)
    is_account_user: Optional[bool] = Field(default=False)
    created_by: str = Field(description="Created by user identifier.")
    created_at: str = Field(description="Creation date timestamp.")
    updated_by: str = Field(description="Last user update identifier.")
    updated_at: str = Field(description="Last updated date timestamp.")


class GetUserSuccessResponse(SuccessResponse):
    users: List[UserObject] = Field(description="Result users list.")


class QueryParams(BaseModel):
    cognito_user_id: Optional[str] = Field(description="User unique identifier.")
    email: Optional[str] = Field(description="User email filter.")
    full_name: Optional[str] = Field(description="User like name.")
    account_id: Optional[str] = Field(description="Users account identifier.")
    is_active: Optional[bool] = Field(description="Are users active.", default=True)
    page: Optional[int] = Field(description="Page number result.")
    per_page: Optional[int] = Field(description="Page results limit.")


DATA_CONTRACT = DataContract(
    request=Request(query_params=QueryParams),
    responses=[
        Response(
            status_code=HTTPStatus.OK,
            description="Get users successfully.",
            body=GetUserSuccessResponse,
        ),
        Response(
            status_code=HTTPStatus.BAD_REQUEST,
            description="Error during users get process.",
            body=ErrorResponse,
        ),
    ],
)
