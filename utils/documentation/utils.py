from typing import Callable

from utils.documentation.models import Docs


def docs(method: str):
    """
    Decorator to annotate Lambda handler functions with OpenAPI metadata.
    """

    def decorator(docs: Docs):
        def wrapper(func: Callable):
            func._docs_metadata = {
                "method": method,
                "path": docs.path,
                "summary": docs.summary,
                "description": docs.summary,
                "responses": {
                    res.status_code: {"description": res.description, "body": res.body}
                    for res in docs.data_contract.responses
                },
                "request": {
                    "body": docs.data_contract.request.body,
                    "query_params": docs.data_contract.request.query_params,
                    "path_params": docs.data_contract.request.path_params,
                }
                or {},
                "tags": docs.tags or [],
                "headers": {},
                "security": docs.security,
            }
            return func

        return wrapper

    return decorator


# Define HTTP method-specific decorators
docs.get = docs("get")
docs.post = docs("post")
docs.put = docs("put")
docs.delete = docs("delete")
docs.patch = docs("patch")
