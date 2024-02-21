from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreationUserAudit(BaseModel):
    created_at: Optional[datetime]
    created_by_user_id: Optional[str]
    created_by_user_name: Optional[str]


class UpdateUserAudit(BaseModel):
    updated_at: Optional[datetime]
    updated_by_user_id: Optional[str]
    updated_by_user_name: Optional[str]


class AuditData(BaseModel):
    created: CreationUserAudit
    updated: UpdateUserAudit


class ResponseModel(BaseModel):
    correlation_id: str
    result: str


class RequestEventModel(BaseModel):
    user_id: str
    tenant_id: str
