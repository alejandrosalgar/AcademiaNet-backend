from typing import Callable, Dict, List


def docs(method: str):
    """
    Decorator to annotate Lambda handler functions with OpenAPI metadata.
    """

    def decorator(
        path: str,
        summary: str,
        description: str,
        responses: Dict,
        request: Dict = None,
        tags: List[str] = None,
        auth: bool = True,
        headers: Dict = None,
    ):
        def wrapper(func: Callable):
            func._docs_metadata = {
                "method": method,
                "path": path,
                "summary": summary,
                "description": description,
                "responses": responses,
                "request": request or {},
                "tags": tags or [],
                "auth": auth,
                "headers": headers or {},
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
