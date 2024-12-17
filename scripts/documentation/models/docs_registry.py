from typing import Dict, List, Set

from openapi_pydantic.util import PydanticSchema
from openapi_pydantic.v3 import (
    OAuthFlow,
    OAuthFlows,
    Operation,
    Parameter,
    PathItem,
    Paths,
    RequestBody,
    Response,
    Responses,
    SecurityRequirement,
    SecurityScheme,
)
from pydantic import BaseModel


class DocsRegistry:
    """
    A utility class to collect and aggregate OpenAPI documentation metadata.
    """

    def __init__(self):
        self.paths: Dict[str, Dict[str, Dict, List]] = {}
        self.tags: Set = set()
        self.security_components: Dict[str, SecurityScheme] = {}

    def add_entry(self, metadata: Dict):
        """Add documentation metadata to the registry."""
        path = metadata.pop("path")
        method = metadata.pop("method")
        if path not in self.paths:
            self.paths[path] = {}
        security = self.update_security_components(metadata.get("security"))
        metadata["security"] = security
        self.paths[path][method] = metadata
        self.tags.update(metadata.get("tags", []))

    @staticmethod
    def __build_security_scheme(scheme: Dict):
        """Build a Pydantic SecurityScheme from a dictionary."""
        if flows := scheme.get("flows"):
            args = {}
            if client_credentials := flows.get("clientCredentials"):
                args["clientCredentials"] = OAuthFlow(**client_credentials)
            elif authorization_code := flows.get("authorizationCode"):
                args["authorizationCode"] = OAuthFlow(**authorization_code)
            scheme["flows"] = OAuthFlows(**args)

        return SecurityScheme(**scheme)

    def update_security_components(self, security: List[List[str]]) -> List[SecurityRequirement]:
        """Update security components and return metadata security."""
        if not security:
            return []

        metadata_security = []
        metadata_security_item: SecurityRequirement = {}

        for security_config in security:
            metadata_security_item = {}
            for security_scheme in security_config:
                scheme = security_scheme.get_component()
                scheme_id = scheme.pop("id")
                self.security_components[scheme_id] = DocsRegistry.__build_security_scheme(scheme)
                metadata_security_item[scheme_id] = security_scheme.scopes
            metadata_security.append(metadata_security_item)

        return metadata_security

    @staticmethod
    def __get_request_body_metadata(request: Dict[str, BaseModel], key: str) -> RequestBody:
        if not request.get(key) or type(request.get(key)).__name__ != "ModelMetaclass":
            return {}
        return RequestBody(
            content={"application/json": {"schema": PydanticSchema(schema_class=request.get(key))}}
        )

    @staticmethod
    def __get_request_params_metadata(request: Dict[str, BaseModel]) -> List[Parameter]:
        if not request.get("path_params"):
            return []
        json_schema: Dict[str, Dict] = request.get("path_params").model_json_schema()
        return [
            Parameter(
                name=name,
                param_in="path",
                required=True,
                description=config.description,
                param_schema=json_schema.get("properties", {}).get(name, {}),
            )
            for name, config in PydanticSchema(
                schema_class=request.get("path_params")
            ).schema_class.model_fields.items()
        ]

    @staticmethod
    def __get_responses(responses: Dict[str, Dict[str, str | BaseModel]]) -> Responses:
        if not responses:
            return Responses()
        return {
            str(status_code): Response(
                description=response_metadata.get("description", "default"),
                content={
                    "application/json": {
                        "schema": PydanticSchema(schema_class=response_metadata.get("body"))
                    }
                },
            )
            for status_code, response_metadata in responses.items()
        }

    def get_paths(self) -> Paths:
        """Retrieve the aggregated OpenAPI paths."""
        openapi_paths: Paths = {}
        for path, methods in self.paths.items():
            optional_parameters = [
                {
                    "method": method,
                    "description": metadata.get("description", "default"),
                    "requestBody": DocsRegistry.__get_request_body_metadata(
                        metadata.get("request"), "body"
                    ),
                    "parameters": DocsRegistry.__get_request_params_metadata(
                        metadata.get("request")
                    ),
                    "responses": DocsRegistry.__get_responses(metadata.get("responses", {})),
                    "tags": metadata.get("tags", []),
                    "summary": metadata.get("summary", "default"),
                    "security": metadata.get("security", []),
                }
                for method, metadata in methods.items()
            ]

            openapi_path = PathItem(
                **{
                    metadata.pop("method"): Operation(
                        **{attr: param for attr, param in metadata.items() if param},
                    )
                    for metadata in optional_parameters
                }
            )
            openapi_paths[path] = openapi_path
        return openapi_paths
