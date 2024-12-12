import os

import custom_logger
from core_utils.boto3_utils.constants import REGION_NAME, RESOURCE_METHOD
from core_utils.boto3_utils.dynamodb import DYNAMO_RESOURCE
from core_utils.boto3_utils.secrets_manager import get_secret
from core_utils.constants import get_globals
from custom_logger.coralogix.repository import CoralogixRepository
from custom_logger.logger.control_center import ControlCenterRepository


def _get_coralogix_secrets(coralogix_secrets: str) -> tuple:
    coralogix_data = get_secret(coralogix_secrets, REGION_NAME, None)
    return coralogix_data.get("CoralogixKey", None), coralogix_data.get("CoralogixUrl", None)


APP_NAME = os.getenv("APP_NAME", "unit_tests")
SERVICE_NAME = os.getenv("SERVICE", "unit_tests_service")
CUSTOM_LOGGER_TABLE = os.getenv("CUSTOM_LOGGER_TABLE_NAME", None)
CONTROL_CENTER_TABLE = DYNAMO_RESOURCE.Table(CUSTOM_LOGGER_TABLE) if CUSTOM_LOGGER_TABLE else None
CORALOGIX_SECRETS = os.getenv("CORALOGIX_SECRET", None)
CORALOGIX_KEY, CORALOGIX_URL = (
    _get_coralogix_secrets(CORALOGIX_SECRETS) if CORALOGIX_SECRETS else (None, None)
)


class LocalControlCenter:
    def get_item(self, *args, **kwargs):
        return {"Item": None}


def initialize_logging():
    custom_logger.setup_default_logger_configuration(
        (
            ControlCenterRepository(CONTROL_CENTER_TABLE, SERVICE_NAME)
            if CUSTOM_LOGGER_TABLE
            else ControlCenterRepository(LocalControlCenter())
        ),
        (
            CoralogixRepository(APP_NAME, CORALOGIX_URL, CORALOGIX_KEY, RESOURCE_METHOD)
            if CORALOGIX_KEY
            else None
        ),
        RESOURCE_METHOD,
    )
    custom_logger.set_message_context({"correlation_id": get_globals()["UUID"]})
    custom_logger.register_white_list_fields(["traceback", "error", "message"])
