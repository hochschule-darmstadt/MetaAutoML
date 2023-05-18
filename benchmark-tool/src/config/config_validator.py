from config import config_accessor
from external.file_system import is_dir


def validate_config_values() -> str | None:
    try:
        config_accessor.get_omaml_server_host()
        config_accessor.get_omaml_server_port()
        config_accessor.get_disable_certificate_check()
        config_accessor.get_userid()
        datasetLocation = config_accessor.get_omaml_dataset_location()
        if not is_dir(datasetLocation):
            return "OMAML_DATASET_LOCATION is not a directory"
    except ValueError as e:
        return str(e)
    return None
