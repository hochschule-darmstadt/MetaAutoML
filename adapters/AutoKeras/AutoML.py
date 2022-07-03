import json
import os.path

from JsonUtil import get_config_property

from AutoKerasAdapter import AutoKerasAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    file_path = os.path.join(get_config_property("job-file-path"),
                             get_config_property("job-file-name"))
    with open(file_path) as file:
        process_json = json.load(file)

    adapter = AutoKerasAdapter(process_json)
    adapter.start()
