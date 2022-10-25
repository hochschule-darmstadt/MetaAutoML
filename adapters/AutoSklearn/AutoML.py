import json
import os
from JsonUtil import get_config_property
import sys
from AutoSklearnAdapter import AutoSklearnAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and start the background AutoML process
    """
    job_file_location = os.path.join(sys.argv[1],
                                        get_config_property("job-file-name"))
    with open(job_file_location) as file:
        process_json = json.load(file)

    process_json["dataset_configuration"] = json.loads(process_json["dataset_configuration"])
    autoML = AutoSklearnAdapter(process_json)

    autoML.start()