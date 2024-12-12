from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(..., description="Code error, e.i. format: {Service}.{CodeError}")
    message: str = Field(..., description="Message error.")
    correlation_id: str = Field(..., description="Process UUID.")
