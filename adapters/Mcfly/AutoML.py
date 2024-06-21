import json
import os.path
import sys

from McflyAdapter import McflyAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and start the background AutoML process
    """
    job_file_location = os.path.join(sys.argv[1],
                                        os.getenv("JOB_FILE_NAME"))
    with open(job_file_location) as file:
        process_json = json.load(file)

    process_json["dataset_configuration"] = json.loads(process_json["dataset_configuration"])
    adapter = McflyAdapter(process_json)
    adapter.start()
