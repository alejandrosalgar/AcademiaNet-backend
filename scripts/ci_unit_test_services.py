import os
import sys


def read_file(file_name: str) -> str:
    if not os.path.exists(file_name):
        return ""
    _file = open(file_name, "r")
    file_content = _file.readlines()
    _file.close()
    return file_content


def parse_file_content_to_list(requirements: str) -> set:
    """_summary_
    Return a set of requirements that are available for the given service
    Args:
        requirements (str): requirements.txt file content

    Returns:
        set: set of requirements that are available for the given service
    """
    return set([requirement.rstrip("\n") for requirement in requirements])


def get_service_folder_name(file_path: str) -> str:
    path_listed = file_path.split("/")
    service_path = ""
    if "services/" in file_path:
        service_path = "/".join(path_listed[: path_listed.index("services") + 2])
    return service_path


def get_services_list() -> list:
    files = set()
    for file_argv_pos in range(1, len(sys.argv)):
        files.add(get_service_folder_name(sys.argv[file_argv_pos]))
    return list(files)


def get_service_libraries(service_path: str, requirements_file_name: str) -> set:
    if os.path.exists(service_path + "/unit"):
        requirements_path = service_path + f"/{requirements_file_name}"
        requirements = read_file(requirements_path)
        return parse_file_content_to_list(requirements)
    else:
        return set()


def create_requirements_file(services_list: list):
    """_summary_
    This function performs a process of creating a requirement.txt file
    with all unit tests dependencies for the github actions job.
    """
    requirements_file_name = "requirements.txt"
    requirements = parse_file_content_to_list(read_file(requirements_file_name))
    for service_path in services_list:
        requirements = requirements | get_service_libraries(service_path, requirements_file_name)

    with open(requirements_file_name, "w") as file:
        for requirement in requirements:
            file.write(requirement + "\n")


def perform():
    services_list = get_services_list()
    create_requirements_file(services_list)
    services_list_str = " ".join(services_list)
    print(services_list_str)  # output for the bash command


if __name__ == "__main__":
    perform()
