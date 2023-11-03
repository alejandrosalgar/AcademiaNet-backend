from core_utils.sql_handler.sql_builder import SQLOperator


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
                            "resource_arn": credential.get("db_cluster_arn"),
                            "secret_arn": credential.get("db_credentials_secrets_store_arn"),
                        },
                        "transaction_params": {
                            "resource_arn": credential.get("db_cluster_arn"),
                            "secret_arn": credential.get("db_credentials_secrets_store_arn"),
                        },
                    }
                )
            else:
                credentials[0]["tenant_id"] = credential.get("tenant_id")
