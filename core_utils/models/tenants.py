from datetime import datetime
from typing import ClassVar

from pydantic import Field

from core_utils.sql_handler.sql_builder import CustomBaseModel, SQLOperator


class TenantNotFoundException(Exception):
    """Tenant not found exception"""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class Tenants(CustomBaseModel):
    table: ClassVar[str] = "tenants_master"
    primary_key: ClassVar[str] = "tenant_id"

    tenant_id: str = Field(frozen=True, max_length=100)
    user_pool_id: str = Field(max_length=70)
    identity_pool_id: str = Field(max_length=70)
    user_pool_client_id: str = Field(max_length=70)
    tenant_name: str = Field(max_length=100)
    database_name: str = Field(default=None, max_length=100)
    db_cluster_arn: str = Field(default=None, max_length=100)
    db_credentials_secrets_store_arn: str = Field(default=None, max_length=100)
    admin_email: str = Field(default=None, max_length=100)
    subdomain: str = Field(default=None, max_length=100)
    admin_email: str = Field(default=None, max_length=100)
    admin_first_name: str = Field(default=None, max_length=70)
    admin_last_name: str = Field(default=None, max_length=70)
    activation_date: datetime | str = Field(default=datetime.now().strftime("%Y-%m-%d"))
    admin_last_name: str = Field(default=None, max_length=70)
    is_active: bool = Field(default=True)
    is_master_tenant: bool = Field(default=False)
    status: str = Field(default=None, max_length=50)
    tenant_bucket: str = Field(default=None, max_length=100)
    created_by: str = Field(frozen=True, max_length=100)
    updated_by: str = Field(frozen=True, max_length=100)

    def get_by_id(self) -> "Tenants":
        filter_obj = self.dict(include={"tenant_id"})
        tenant = SQLOperator.select_model(self, **filter_obj)
        if not tenant:
            raise TenantNotFoundException(message=(f"Tenant with id {self.tenant_id} not found"))
        return tenant[0]

    def get_tenants_db_credentials(self) -> list:
        default_credentials = {"tenant_id": None, "rds_params": {}, "transaction_params": {}}
        data = SQLOperator.select_model(self, is_active=True)
        credentials = [default_credentials]
        if not data:
            return credentials
        else:
            for credential in data:
                if credential.get("database_name"):
                    credentials.append(
                        {
                            "tenant_id": credential.get("tenant_id"),
                            "rds_params": {
                                "database": credential.get("database_name"),
                                "resourceArn": credential.get("db_cluster_arn"),
                                "secretArn": credential.get("db_credentials_secrets_store_arn"),
                            },
                            "transaction_params": {
                                "resourceArn": credential.get("db_cluster_arn"),
                                "secretArn": credential.get("db_credentials_secrets_store_arn"),
                            },
                        }
                    )
                else:
                    credentials[0]["tenant_id"] = credential.get("tenant_id")
