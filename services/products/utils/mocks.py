from unittest.mock import patch


def tenant_setup_mock(fn):
    def wrapper(*args, **kwargs):
        response = fn(*args, **kwargs)
        return response

    return wrapper


def lambda_decorator_mock(fn):
    def wrapper(*args, **kwargs):
        response = fn(*args, **kwargs)
        return response

    return wrapper


def webhook_dispatch_mock(object_name=None, action=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return decorator


mock_decorators = {
    "tenant_setup": tenant_setup_mock,
    "lambda_decorator": lambda_decorator_mock,
    "webhook_dispatch": webhook_dispatch_mock,
}


def mock_decorator(decorator):
    patch(f"core_utils.http_utils.api_handler.{decorator}", mock_decorators[decorator]).start()
