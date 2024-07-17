import json
import os
import logging
import sys

from AutoPytorchAdapter import AutoPytorchAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=FORMAT)

    job_file_location = os.path.join(sys.argv[1],
                                        os.getenv("JOB_FILE_NAME"))
    with open(job_file_location) as file:
        process_json = json.load(file)

    process_json["dataset_configuration"] = json.loads(process_json["dataset_configuration"])

    autoMl = AutoPytorchAdapter(process_json)
    autoMl.start()
