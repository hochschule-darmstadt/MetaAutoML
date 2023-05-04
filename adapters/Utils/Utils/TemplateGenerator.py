from jinja2 import Template

import os
from JsonUtil import get_config_property
import json

class TemplateGenerator(object):
    """
    Template generator to generate the custom AutoML output
    """

    def __init__(self, config):
        """
        Init a new instance of TemplateGenerator
        """
        self.__TEMPLATES_PATH = get_config_property("templates-path")
        self.__OUTPUT_PATH = config.result_folder_location
        self._configuration = config
        self._configuration.dataset_configuration = json.loads(self._configuration.dataset_configuration)
        return

    def generate_script(self):
        """
        Generate the AutoML specific scripts to execute the generated model
        ---
        Parameter:
        1. ML task
        """

        # Render Python script
        with open(os.path.join(self.__TEMPLATES_PATH, 'predict.ji')) as file:
            template = Template(file.read())
        with open(os.path.join(self.__OUTPUT_PATH, 'predict.py'), "w") as script_file:
            script_file.write(template.render(configuration=self._configuration))

        # Render Requirement.txt
        with open(os.path.join(self.__TEMPLATES_PATH, 'requirements.ji')) as file:
            template = Template(file.read())
        with open(os.path.join(self.__OUTPUT_PATH, 'requirements.txt'), "w") as script_file:
            script_file.write(template.render(configuration=self._configuration))

        if get_config_property("local_execution") == "YES":
            #During development the shared template files are saved centralized
            self.__TEMPLATES_PATH = "../Utils/Templates"

        # Render Python preprocessing script
        with open(os.path.join(self.__TEMPLATES_PATH, 'preprocessing.ji')) as file:
            template = Template(file.read())
        with open(os.path.join(self.__OUTPUT_PATH, 'preprocessing.py'), "w") as script_file:
            script_file.write(template.render(configuration=self._configuration))

        # Render Python dataset script
        with open(os.path.join(self.__TEMPLATES_PATH, 'dataset.ji')) as file:
            template = Template(file.read(), trim_blocks=True, lstrip_blocks=True)
        with open(os.path.join(self.__OUTPUT_PATH, 'dataset.py'), "w") as script_file:
            script_file.write(template.render(configuration=self._configuration))
