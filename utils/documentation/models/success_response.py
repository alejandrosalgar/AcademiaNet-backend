from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    result: str = Field(..., description="Response description.")
    correlation_id: str = Field(..., description="Process UUID.")
