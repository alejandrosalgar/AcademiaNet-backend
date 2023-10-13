from typing import ClassVar

from pydantic import Field, List

from core_utils.sql_handler.sql_builder import CustomBaseModel, SQLOperator


class TenantKeyNotFoundException(Exception):
    """Tenant key not found exception"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class TenantKeys(CustomBaseModel):
    table: ClassVar[str] = "tenant_keys"
    primary_key: ClassVar[str] = "tenant_key_id"

    tenant_key_id: str = Field(frozen=True, max_length=100)
    tenant_id: str = Field(max_length=100)
    secret_arn: str = Field(max_length=100)
    secret_name: str = Field(max_length=100)
    secret_version: str = Field(max_length=100)
    created_by: str = Field(frozen=True, max_length=100)
    updated_by: str = Field(frozen=True, max_length=100)

    def get_by_tenant_id(self) -> List["TenantKeys"]:
        filter_obj = self.dict(include={"tenant_id"})
        tenant_key = SQLOperator.select_model(self, **filter_obj)
        if not tenant_key:
            raise TenantKeyNotFoundException(
                message=(f"Tenant key with id {self.tenant_key_id} not found")
            )
        return tenant_key
