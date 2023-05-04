from config.config_adapter import get_config_value as __get_config_value


def get_userid():
    return __get_config_value("BENCHMARK_USERID")


def get_omaml_server_host():
    host = __get_config_value("OMAML_SERVER_HOST")
    if host is None:
        raise ValueError("OMAML_SERVER_HOST is not set")
    return host


def get_omaml_server_port():
    port = __get_config_value("OMAML_SERVER_PORT")
    if port is None:
        raise ValueError("OMAML_SERVER_PORT is not set")
    return int(port)
