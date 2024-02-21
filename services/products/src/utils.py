from enum import StrEnum
from custom_logger.coralogix.repository import CoralogixRepository
from custom_logger.logger.control_center import ControlCenterRepository
from core_utils.boto3_utils.dynamodb import DYNAMO_RESOURCE
from core_utils.boto3_utils.secrets_manager import get_secret
from core_utils.boto3_utils.constants import REGION_NAME, RESOURCE_METHOD
from core_utils.constants import get_globals
import custom_logger
import os

APP_NAME = os.environ["APP_NAME"]
SERVICE_NAME = os.environ["SERVICE_NAME"]
CONTROL_CENTER_TABLE = DYNAMO_RESOURCE.Table(os.environ["CUSTOM_LOGGER_TABLE_NAME"])
CORALOGIX_URL = os.environ["CORALOGIX_URL"]
CORALOGIX_KEY_SECRET_NAME = os.environ["CORALOGIX_KEY_SECRET_NAME"]
CORALOGIX_KEY = get_secret(CORALOGIX_KEY_SECRET_NAME, REGION_NAME, "CoralogixKey")


class Components(StrEnum):
    USERS = "users"
    GENERAL = "general"
    PRODUCTS = "products"


def initialize_logging():
    custom_logger.setup_default_logger_configuration(
        ControlCenterRepository(CONTROL_CENTER_TABLE, SERVICE_NAME),
        CoralogixRepository(APP_NAME, CORALOGIX_URL, CORALOGIX_KEY, RESOURCE_METHOD),
        RESOURCE_METHOD,
    )
    custom_logger.set_message_context({"correlation_id": get_globals()["UUID"]})
