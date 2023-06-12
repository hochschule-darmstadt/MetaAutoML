import json
import os
import logging
import sys

from GAMAAdapter import GAMAAdapter
from JsonUtil import get_config_property

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and start the background AutoML process
    """
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

    job_file_location = os.path.join(sys.argv[1],
                                        get_config_property("job-file-name"))
                                        
    with open(job_file_location) as file:
        process_json = json.load(file)

    process_json["dataset_configuration"] = json.loads(process_json["dataset_configuration"])
    autoML = GAMAAdapter(process_json)
    autoML.start()
