import json
import os.path
import sys
from JsonUtil import get_config_property

from McflyAdapter import McflyAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    job_file_location = os.path.join(sys.argv[1],
                                        get_config_property("job-file-name"))
    with open(job_file_location) as file:
        process_json = json.load(file)

    process_json["dataset_configuration"] = json.loads(process_json["dataset_configuration"])
    adapter = McflyAdapter(process_json)
    adapter.start()
