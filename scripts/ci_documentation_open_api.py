import os
import sys

import yaml
from documentation.compile_docs import collect_docs
from documentation.models.docs_registry import DocsRegistry
from openapi_pydantic.util import construct_open_api_with_schema_class
from openapi_pydantic.v3 import Components, Contact, Info, License, OpenAPI, Server, Tag


def _add_to_path(path):
    # note: this script allow to support relative modules importing
    path_to_add = path

    for _ in range(0, 3):
        path_to_add = os.path.dirname(path_to_add)

    sys.path.append(path_to_add)


def _delete_last_added_path():
    sys.path.pop()


# Constants for environment variables
SERVER_URL = os.getenv("SERVER_URL", "https://htxoulxfxc.execute-api.us-east-2.amazonaws.com/dev")
OPENAPI_VERSION = os.getenv("OPENAPI_VERSION", "3.1.0")
DOCS_TITLE = os.getenv("DOCS_TITLE", "API Documentation")
DOCS_VERSION = os.getenv("DOCS_VERSION", "1.0.0")
SERVER_DESCRIPTION = os.getenv("SERVER_DESCRIPTION", "Development Server")
DOCS_OUTPUT_PATH = os.getenv("DOCS_OUTPUT_PATH", "open_api.yaml")


# OpenAPI Docs Registry
docs_registry = DocsRegistry()


def generate_open_api_documentation() -> OpenAPI:
    """
    Generate OpenAPI documentation by scanning for `@docs` decorators
    in the services folder.
    """

    docs_registry = collect_docs()
    # Build OpenAPI spec from registry
    openapi_spec = OpenAPI(
        openapi=OPENAPI_VERSION,
        info=Info(
            title=DOCS_TITLE,
            version=DOCS_VERSION,
            description=SERVER_DESCRIPTION,
            termsOfService="http://example.com/terms/",
            contact=Contact(name="API Documentation", email="api-documentation@example.com"),
            license=License(name="MIT License", url="https://opensource.org/licenses/MIT"),
        ),
        tags=[Tag(name=tag) for tag in docs_registry.tags],
        servers=[Server(url=SERVER_URL)],
        paths=docs_registry.get_paths(),
        components=Components(securitySchemes=docs_registry.security_components),
    )

    return openapi_spec


if __name__ == "__main__":
    # Generate OpenAPI documentation
    open_api_spec = generate_open_api_documentation()
    open_api = construct_open_api_with_schema_class(open_api_spec)

    # Save to file
    with open(DOCS_OUTPUT_PATH, "w") as file:
        file.write(
            yaml.dump(
                open_api.model_dump(
                    by_alias=True,
                    mode="json",
                    exclude_none=True,
                    exclude_unset=True,
                ),
                sort_keys=False,
            )
        )

    print(f"OpenAPI documentation generated at {DOCS_OUTPUT_PATH}")
