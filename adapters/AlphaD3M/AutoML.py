import json
import os.path

from JsonUtil import get_config_property

from AutoMLs.AlphaD3MAdapter import AlphaD3MAdapter

if __name__ == '__main__':
    """
    Entry point for the AutoML subprocess, read configuration json and execute the correct AutoML task
    """
    file_path = os.path.join(get_config_property("job-file-path"),
                             get_config_property("job-file-name"))
    with open(file_path) as file:
        process_json = json.load(file)

    adapter = AlphaD3MAdapter(process_json)
    adapter.start()
