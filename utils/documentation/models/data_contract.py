from http import HTTPStatus
from typing import Any, List

from pydantic import BaseModel, Field

from utils.documentation.models.error_response import ErrorResponse
from utils.documentation.models.security import DEFATULT_AUTH, ApiSecurityScheme


class Response(BaseModel):
    status_code: HTTPStatus
    description: str
    body: Any


class Request(BaseModel):
    body: Any = Field(default={})
    query_params: Any = Field(default={})
    path_params: Any = Field(default={})


class DataContract(BaseModel):
    """
    Base model for data contracts.
    """

    request: Request
    responses: List[Response]

    def model_post_init(self, __context):
        self.responses.append(
            Response(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                description="Internal Code Error.",
                body=ErrorResponse,
            ),
        )
        return super().model_post_init(__context)


class Docs(BaseModel):
    """Base model for docs metadata"""

    path: str
    summary: str
    description: str
    data_contract: DataContract
    tags: List[str]
    security: List[List[ApiSecurityScheme]] = DEFATULT_AUTH  # set as [] if not auth
