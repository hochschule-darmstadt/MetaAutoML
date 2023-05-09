from config.config_adapter import get_config_value as __get_config_value


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
