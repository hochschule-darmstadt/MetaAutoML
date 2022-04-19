import json
import os
import logging
import sys

from TabularDataAutoML import TabularDataAutoML
from JsonUtil import get_config_property

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

    file_path = os.path.join(get_config_property("job-file-path"),
                             get_config_property("job-file-name"))
    with open(file_path) as file:
        process_json = json.load(file)

    tabularDataAutoML = TabularDataAutoML(process_json)
    tabularDataAutoML.execute_task()
