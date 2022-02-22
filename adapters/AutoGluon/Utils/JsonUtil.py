import json


def get_config_property(property_name: str):
    with open("./config.json", "r") as config_file:
        data = json.load(config_file)

    return data[property_name]
