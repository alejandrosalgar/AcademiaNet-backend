import uuid
from datetime import datetime

UUID = uuid.uuid4().hex
CURRENT_DATETIME = datetime.now()


def user_agent_handler(user_agent: str):
    global USER_AGENT
    USER_AGENT = user_agent


HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET,HEAD,OPTIONS,POST,PUT,DELETE",
    "Access-Control-Allow-Headers": (
        "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With,"
        " Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"
    ),
}

CHARSET = "UTF-8"
