import os
import shutil

layers = {
    "utils": {"src": "utils", "zip_name": "Utils"},
}

# submodules = submodules = [f"src/{f}" for f in os.listdir("src")]
submodules = []

ignore_folders = ["unit", "migrations_sql"]


def create_local_layer(services_path="", layer_src=""):
    services_paths = [
        f"{services_path}/{service}"
        for service in os.listdir(f"{services_path}")
        if "." not in service and service not in ignore_folders
    ]
    for service_path in services_paths:
        layer_path = f"{service_path}/{layer_src}"
        if os.path.exists(layer_path):
            shutil.rmtree(layer_path)
        shutil.copytree(layer_src, layer_path)


def create_layers_flow():
    """
    Create python script for layer standard creation and local layers
    """
    layer_folder = "layer"
    os.makedirs(layer_folder)
    python_folder = "python"
    os.makedirs(f"{layer_folder}/{python_folder}")

    for layer_name in layers:
        # Zip layers
        layer = layers[layer_name]
        shutil.copytree(layer["src"], f"{layer_folder}/{python_folder}/{layer['src']}")
        shutil.make_archive(layer["zip_name"], "zip", layer_folder)
        shutil.rmtree(f"{layer_folder}/{python_folder}/{layer['src']}")
        # Create local layers per each service
        create_local_layer(services_path="services", layer_src=layer["src"])
        for submodule in submodules:
            create_local_layer(services_path=submodule, layer_src=layer["src"])
    shutil.rmtree(layer_folder)


if __name__ == "__main__":
    create_layers_flow()
