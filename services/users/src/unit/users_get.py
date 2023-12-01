from core_utils.mocks import http_event_mock
from core_utils.boto3_utils.constants import setup_aws_session
from functions.users_get import lambda_handler
import os

fpath = "../../sls/aws_data.env"

setup_aws_session(os.path.abspath(fpath))

def test_users_get():
    event = http_event_mock(
        user_id="845d59af-036f-48fc-8f1a-26630a7af8e0",
    )
    res = lambda_handler(event, None)
    print(res)
