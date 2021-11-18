import json
import os
import logging
import sys

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML
from JsonUtil import get_config_property

if __name__ == '__main__':
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

    json_file = open(get_config_property("job-file-name"))
    processJson = json.load(json_file)

    structuredDataAutoML = StructuredDataAutoML(processJson)
    structuredDataAutoML.execute_task()
