import json
import os.path
from JsonUtil import get_config_property
import sys
from MLJARAdapter import MLJARAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and start the background AutoML process
    """
    job_file_location = os.path.join(sys.argv[1],
                                        get_config_property("job-file-name"))
    with open(job_file_location) as file:
        process_json = json.load(file)
    process_json["dataset_configuration"] = json.loads(process_json["dataset_configuration"])

    autoMl = MLJARAdapter(process_json)
    autoMl.start()
