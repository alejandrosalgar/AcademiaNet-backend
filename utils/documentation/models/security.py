import os
from enum import StrEnum
from typing import List

from pydantic import BaseModel


class SecuritySchemeTypes(StrEnum):
    HTTP = "http"
    BEARER = "bearer"
    API_KEY = "apiKey"
    APP_KEY = "appKey"
    TENANT_KEY = "tenantKey"
    OPEN_ID = "openIdConnect"
    OAUTH_2 = "oauth2"
    TENANT_ID = "tenant_id"


class ApiScopes(StrEnum):
    JSON_READ = "apiauthidentifier/json.read"
    COGNITO = "aws.cognito.signin.user.admin"


class ApiSecurityScheme(BaseModel):
    """
    Security headers for the API.
    """

    authorization: SecuritySchemeTypes
    scopes: List[str] = []

    def get_component(self):
        """
        Post-initialization hook.
        """
        match self.authorization:
            case SecuritySchemeTypes.HTTP:
                return {
                    "id": SecuritySchemeTypes.HTTP,
                    "type": self.authorization.value,
                    "scheme": "basic",
                }
            case SecuritySchemeTypes.BEARER:
                return {
                    "id": SecuritySchemeTypes.BEARER,
                    "type": "http",
                    "scheme": self.authorization.value,
                }
            case SecuritySchemeTypes.API_KEY:
                return {
                    "id": SecuritySchemeTypes.API_KEY,
                    "type": self.authorization.value,
                    "name": "X-API-Key",
                    "in": "header",
                }
            case SecuritySchemeTypes.APP_KEY:
                return {
                    "id": SecuritySchemeTypes.APP_KEY,
                    "type": "apiKey",
                    "name": "App-Key",
                    "in": "header",
                }
            case SecuritySchemeTypes.TENANT_KEY:
                return {
                    "id": SecuritySchemeTypes.TENANT_KEY,
                    "type": "apiKey",
                    "name": "Tenant-Key",
                    "in": "header",
                }
            case SecuritySchemeTypes.TENANT_ID:
                return {
                    "id": SecuritySchemeTypes.TENANT_ID,
                    "type": "apiKey",
                    "name": "tenant_id",
                    "in": "header",
                }
            case SecuritySchemeTypes.OPEN_ID:
                return {
                    "id": SecuritySchemeTypes.OPEN_ID,
                    "type": self.authorization.value,
                    "openIdConnectUrl": os.getenv("OPEN_ID_URL", "http://example.com/auth/openid"),
                }
            case SecuritySchemeTypes.OAUTH_2:
                return {
                    "id": SecuritySchemeTypes.OAUTH_2,
                    "type": self.authorization.value,
                    "flows": {
                        "clientCredentials": {
                            "authorizationUrl": os.getenv(
                                "OAUTH_2_AUTH_URL", "http://example.com/auth/authorize"
                            ),
                            "tokenUrl": os.getenv(
                                "OAUTH_2_TOKEN_URL",
                                "https://pocbackendcoredevappkeys.auth.us-east-2.amazoncognito.com/oauth2/token",
                            ),
                            "refreshUrl": os.getenv(
                                "OAUTH_2_REFRESH_URL", "http://example.com/auth/refresh"
                            ),
                            "scopes": {scope: "" for scope in self.scopes},
                        }
                    },
                }
        raise Exception(f"Invalid security scheme type {self.authorization}")


DEFATULT_AUTH = [
    # BEARER TOKEN
    [ApiSecurityScheme(authorization=SecuritySchemeTypes.BEARER, scopes=[ApiScopes.COGNITO])],
    # OR
    [  # APP KEY AND OAUTH2
        ApiSecurityScheme(authorization=SecuritySchemeTypes.APP_KEY),
        ApiSecurityScheme(authorization=SecuritySchemeTypes.OAUTH_2, scopes=[ApiScopes.JSON_READ]),
        ApiSecurityScheme(authorization=SecuritySchemeTypes.TENANT_ID),
    ],
    # OR
    [  # TENANT KEY AND OAUTH2
        ApiSecurityScheme(authorization=SecuritySchemeTypes.TENANT_KEY),
        ApiSecurityScheme(authorization=SecuritySchemeTypes.OAUTH_2, scopes=[ApiScopes.JSON_READ]),
    ],
]
