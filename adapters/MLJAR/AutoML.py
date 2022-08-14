import json
import os.path
from JsonUtil import get_config_property
import sys
from MLJARAdapter import MLJARAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    job_file_location = os.path.join(get_config_property("training-path"),
                                        sys.argv[1],
                                        sys.argv[2],
                                        get_config_property("job-folder-name"),
                                        get_config_property("job-file-name"))
    with open(job_file_location) as file:
        process_json = json.load(file)

    autoMl = MLJARAdapter(process_json)
    autoMl.start()
