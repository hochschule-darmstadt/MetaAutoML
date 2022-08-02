import json
import os.path
import sys
from JsonUtil import get_config_property

from AutoMLs.AlphaD3MAdapter import AlphaD3MAdapter

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

    adapter = AlphaD3MAdapter(process_json)
    adapter.start()
