import importlib
import os
import sys
import traceback
from pathlib import Path
from typing import Dict, List

from documentation.models.docs_registry import DocsRegistry

# Path to the services directory
SERVICES_PATH = Path("./services")


def _add_to_path(path):
    # note: this script allow to support relative modules importing
    path_to_add = path

    for _ in range(0, 3):
        path_to_add = os.path.dirname(path_to_add)

    sys.path.append(path_to_add)


def _delete_last_added_path():
    sys.path.pop()


# OpenAPI Docs Registry
docs_registry = DocsRegistry()


def __extract_imports(file: str) -> List[str]:
    """
    Extract all import statements from the source code.
    """
    multi_line_import_flag = False
    module_name = ""
    import_list = []
    file.seek(0)
    for statement in file:
        statement = statement.strip()
        if (
            not statement.startswith("import")
            and not statement.startswith("from")
            and not multi_line_import_flag
        ):
            continue
        module_name += statement
        if statement.endswith(")"):
            multi_line_import_flag = False
            import_list.append(module_name)
            module_name = ""
            continue

        if statement.endswith("(") or statement.endswith(","):
            multi_line_import_flag = True
            continue

        multi_line_import_flag = False
        import_list.append(module_name)
        module_name = ""
    return import_list


def __build_exec_context(import_statements: List[str]) -> Dict:
    """
    Build the execution context with imported dependencies.
    """
    exec_globals = {"__builtins__": __builtins__}
    for indx in range(len(import_statements)):
        statement = import_statements[indx]
        try:
            if statement.startswith("import "):
                # Example: "import os"
                module_name = statement.split()[1]
                exec_globals[module_name] = importlib.import_module(module_name)
            elif statement.startswith("from "):
                # Example: "from pydantic import BaseModel"

                parts = statement.replace(", ", ",").split()
                module_name = parts[1]
                parts[3] = parts[3].replace("(", "").replace(",)", "").replace(")", "")
                imported_names = parts[3].split(",")  # Remove trailing commas
                for imported_name in imported_names:
                    module = importlib.import_module(module_name)
                    exec_globals[imported_name] = getattr(module, imported_name, None)
        except ModuleNotFoundError as e:
            print(f"Module not found for statement '{statement}': {e}")
        except AttributeError as e:
            print(f"Failed to import '{statement}': {e}")
    return exec_globals


def collect_docs() -> DocsRegistry:
    """Collect documention information over all statements"""

    for service_path in SERVICES_PATH.rglob("*/handlers/*.py"):

        with open(service_path, "r", encoding="utf-8") as file:
            source_code = file.read()
            try:
                # Add python path
                _add_to_path(service_path)

                # Extract and process imports
                imports = __extract_imports(file)
                exec_globals = __build_exec_context(imports)

                # Compile and execute the module code
                local_vars = {}
                module = compile(source_code, service_path.name, "exec")
                exec(module, exec_globals, local_vars)

                # Extract and process documented functions
                for _, obj in local_vars.items():
                    if callable(obj) and hasattr(obj, "_docs_metadata"):
                        docs_registry.add_entry(obj._docs_metadata)
                _delete_last_added_path()
            except Exception as e:
                print(f"Error parsing {service_path}: {e} :: traceback {traceback.format_exc()}")

    return docs_registry
