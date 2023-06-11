from config.config_adapter import get_config_value as __get_config_value
from os.path import normpath as __normpath


def get_userid():
    """Gets the value of the configuration option that contains the user id of an existing omaml user.

    Returns:
        str: The user id
    """
    return __get_config_value("BENCHMARK_USERID")


def get_omaml_server_host():
    """Gets the value of the configuaration option that contains the host of the omaml server.

    Raises:
        ValueError: When the configuration option is not set

    Returns:
        str: The host of the omaml server
    """
    host = __get_config_value("OMAML_SERVER_HOST")
    if host is None:
        raise ValueError("OMAML_SERVER_HOST is not set")
    return host


def get_omaml_server_port():
    """Gets the value of the configuration option that contains the port of the omaml server.

    Raises:
        ValueError: When the configuration option is not set

    Returns:
        int: The port of the omaml server
    """
    port = __get_config_value("OMAML_SERVER_PORT")
    if port is None:
        raise ValueError("OMAML_SERVER_PORT is not set")
    return int(port)


def get_disable_certificate_check():
    """Gets the value of the configuration option that contains whether the certificate check should be disabled.
    In production, this should be set to False.

    Returns:
        bool: Whether the certificate check should be disabled
    """
    return __get_config_value("DISABLE_CERTIFICATE_CHECK") == "True"


def get_omaml_dataset_location():
    """Gets the value of the configuration option that contains the location where the omaml controller expects the dataset file to be located.

    Raises:
        ValueError: When the configuration option is not set

    Returns:
        str: The location of the omaml dataset
    """
    location = __get_config_value("OMAML_DATASET_LOCATION")
    if location is None:
        raise ValueError("OMAML_DATASET_LOCATION is not set")
    return __normpath(
        location
    )  # normpath is used to make sure that the path is valid on the current operating system


def get_training_runtime_limit():
    """Gets the value of the configuration option that contains the maximum runtime of a training in seconds.

    Raises:
        ValueError: When the configuration option is not set

    Returns:
        int: The maximum runtime of a training in minutes
    """
    runtime = __get_config_value("TRAINING_RUNTIME_LIMIT")
    if runtime is None:
        raise ValueError("TRAINING_RUNTIME_LIMIT is not set")
    return int(runtime)
