import os
import sys


def _read_file() -> list:
    services_file = open('services_to_deploy.txt', 'r')
    services_to_deploy = services_file.readlines()
    services_file.close()
    return [service.rstrip('\n') for service in services_to_deploy]


def perform() -> None:
    services = _read_file()
    errors = []
    option = sys.argv[1]
    stage = sys.argv[2]
    for service in services:
        if service == 'all':
            result = os.system(f'npx serverless deploy {option} {stage}')
        else:
            result = os.system(
                f'npx serverless {service}:deploy {option} {stage}')
        if result == 1:
            errors.append(service)
    if len(errors):
        print(f'The deployment of these services: {",".join(errors)} failed!')
    else:
        print('All services deployed successfully!')


perform()
