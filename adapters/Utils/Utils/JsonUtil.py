import json
import os

def get_config_property(property_name: str):
    """Get a configuration parameter from the adapters config.json file

    Args:
        property_name (str): The name of the property to retrieve the value from

    Returns:
        _type_: The property value
    """
    config_path = "./config/config.json"
    if os.getenv("USE_DEV_CONFIG") == "YES":
        config_path = "./config/config_development.json"
    with open(config_path, "r") as config_file:
        data = json.load(config_file)

    return data[property_name]
