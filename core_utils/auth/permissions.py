from dataclasses import dataclass

from core_utils.boto3.rds import rds_execute_statement
from core_utils.constants import user_agent_handler
from core_utils.sql_handler.sql_builder import SQLBuilder


class PermissionException(Exception):
    """Exception thrown when permission is denied"""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass
class Permission:
    cognito_user_id: str = None
    tenant_id: str = None
    correlation_uuid: str = None
    module: str = None
    component_name: str = None
    subcomponent: str = None
    action: str = None

    def check_permissions(self) -> None:
        self._check_tenant_permissions()
        self._check_user_permissions()

    def _check_tenant_permissions(self) -> None:
        # Check tenant level permissions
        is_tenant_permitted = self.has_tenant_level_permissions()

        if not is_tenant_permitted:
            raise PermissionException(
                "role_permissions.TenantDoesNotHaveAccessToThisFeature",
                f"Tenant with id {self.tenant_id} doesn't have access to this feature",
            )

    def _check_user_permissions(self) -> None:
        # Check user level permissions
        is_user_permitted = self.has_user_level_permissions()

        if not is_user_permitted:
            raise PermissionException(
                "role_permissions.UserDoesNotHaveAccessToThisFeature",
                f"User with {self.cognito_user_id} does not have access to this feature",
            )

    def has_tenant_level_permissions(self):
        sql = (
            SQLBuilder()
            .select("tenant_permissions tp", ["COUNT(*) as count"])
            .inner_join("components_master c ON tp.components_id = c.components_id ")
            .where(
                [
                    f"tp.tenant_id = '{self.tenant_id}'",
                    f"c.module = '{self.module}'",
                    f"c.component = '{self.component}'",
                    f"c.subcomponent = '{self.subcomponent}'",
                    "c.is_active = TRUE",
                ]
            )
        ).query
        count = rds_execute_statement(sql)[0]["count"]
        if count == 0:
            return False
        else:
            return True

    def has_user_level_permissions(self):
        if (user_agent_handler.__globals__.get("USER_AGENT") == "Tenant Key") or (
            user_agent_handler.__globals__.get("USER_AGENT") == "Application Key"
        ):
            return True
        user_roles_sql = (
            SQLBuilder()
            .select("user_roles", ["role_id"])
            .where([f"cognito_user_id = '{self.cognito_user_id}'"])
            .query
        )
        sql = (
            SQLBuilder()
            .select("role_permissions rp", ["COUNT(*) as count"])
            .inner_join("components_master c ON rp.components_id = c.components_id ")
            .where(
                [
                    f"rp.tenant_id = '{self.tenant_id}'",
                    f"c.module = '{self.module}'",
                    f"c.component = '{self.component}'",
                    f"c.subcomponent = '{self.subcomponent}'",
                    f"rp.role_permissions.{self.action} = TRUE ",
                    "c.is_active = TRUE",
                    f"rp.role_id IN ({user_roles_sql})",
                ]
            )
        ).query
        count = rds_execute_statement(sql)[0]["count"]
        if count == 0:
            return False
        else:
            return True
