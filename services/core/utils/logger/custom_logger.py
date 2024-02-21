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


APP_NAME = os.environ["APP_NAME"]
SERVICE_NAME = os.environ["SERVICE"]
CONTROL_CENTER_TABLE = DYNAMO_RESOURCE.Table(os.environ["CUSTOM_LOGGER_TABLE_NAME"])
CORALOGIX_SECRETS = os.getenv("CORALOGIX_SECRET", None)
CORALOGIX_KEY, CORALOGIX_URL = _get_coralogix_secrets(CORALOGIX_SECRETS)


def initialize_logging():
    custom_logger.setup_default_logger_configuration(
        ControlCenterRepository(CONTROL_CENTER_TABLE, SERVICE_NAME),
        CoralogixRepository(APP_NAME, CORALOGIX_URL, CORALOGIX_KEY, RESOURCE_METHOD),
        RESOURCE_METHOD,
    )
    custom_logger.set_message_context({"correlation_id": get_globals()["UUID"]})
