from datetime import datetime

import requests

CORALOGIX_API = "https://api.coralogix.com/api/v1/logs"


def post_request_async(api, body):
    try:
        requests.post(api, json=body, timeout=0.0000000001)
    except requests.exceptions.ReadTimeout:
        pass


def send_to_coralogix(
    private_key: str,
    logs: str,
    app_name: str,
    subsystem_name: str,
    severity: int,
    computer_name: str = None,
    class_name: str = None,
    category: str = None,
    method_name: str = None,
):
    """This function sends a request to Coralogix with the given data.

    Args:
        private_key (str): Coralogix account private key
        logs (str): The logs text
        app_name (str): Application Name to be shown in Coralogix
        subsystem_name (str): Subsystem Name to be shown in Coralogix
        severity (int): Severity of the logs
            1. Debug, 2. Verbose, 3. Info, 4. Warn,
            5. Error, 6. Critical. Defaults to None.
        computer_name (str, optional): Computer Name to be shown in Coralogix
        class_name (str, optional): Class Name to be shown in Coralogix. Defaults to None.
        category (str, optional): Category to be shown in Coralogix. Defaults to None.
        method_name (str, optional): Method Name to be shown in Coralogix. Defaults to None.
    """
    # Get the datetime and change it to miliseconds
    now = datetime.now()

    data = {
        "privateKey": private_key,
        "applicationName": app_name,
        "subsystemName": subsystem_name,
        "logEntries": [
            {
                "timestamp": now.timestamp() * 1000,  # 1457827957703.342,
                "text": logs,
                "severity": severity,
            }
        ],
    }
    if computer_name:
        data["computerName"] = computer_name
    if class_name:
        data["logEntries"][0]["className"] = class_name
    if category:
        data["logEntries"][0]["category"] = category
    if method_name:
        data["logEntries"][0]["methodName"] = method_name

    # Make the request to coralogix
    post_request_async(CORALOGIX_API, data)
