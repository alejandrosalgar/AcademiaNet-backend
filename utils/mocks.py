from dataclasses import dataclass
from unittest.mock import patch


def lambda_wrapper_mock(
    before=None, after=None, transactional=True, sql_context=None, event_logging_level=None
):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return decorator


mock_decorators = {
    "lambda_wrapper": lambda_wrapper_mock,
}


def mock_decorator(decorator):
    patch(f"core_utils.lambda_utils.{decorator}", mock_decorators[decorator]).start()


@dataclass
class LambdaContext:
    aws_request_id: str = "845d59af-036f-48fc-8f1a-26630a7af8e1"
