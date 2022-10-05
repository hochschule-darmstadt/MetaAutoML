import json
import os
import sys
from JsonUtil import get_config_property

from AutoKerasAdapter import AutoKerasAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    job_file_location = os.path.join(sys.argv[1],
                                        get_config_property("job-file-name"))
    with open(job_file_location) as file:
        process_json = json.load(file)

    adapter = AutoKerasAdapter(process_json)
    adapter.start()
