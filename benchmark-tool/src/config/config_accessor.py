from config.config_adapter import get_config_value as __get_config_value


def get_userid():
    return __get_config_value("BENCHMARK_USERNAME")
