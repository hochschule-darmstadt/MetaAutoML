import json
import os
import logging
import sys

from AutoPytorchAdapter import AutoPytorchAdapter
from JsonUtil import get_config_property

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

    job_file_location = os.path.join(get_config_property("training-path"),
                                        sys.argv[1],
                                        sys.argv[2],
                                        get_config_property("job-folder-name"),
                                        get_config_property("job-file-name"))
    with open(job_file_location) as file:
        process_json = json.load(file)

    autoMl = AutoPytorchAdapter(process_json)
    autoMl.start()
