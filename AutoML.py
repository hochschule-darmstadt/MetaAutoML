import json
from Utils.JsonUtil import get_config_property

from AutoMLs.StructuredDataAutoML import StructuredDataAutoML

if __name__ == '__main__':
    json_file = open(get_config_property("job-file-name"))
    processJson = json.load(json_file)
    structuredDataAutoML = StructuredDataAutoML(processJson)
    structuredDataAutoML.execute_task()
