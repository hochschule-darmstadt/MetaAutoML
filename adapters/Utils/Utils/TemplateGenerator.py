from jinja2 import Template

import os
from JsonUtil import get_config_property


class TemplateGenerator(object):
    """
    Template generator to generate the custom AutoML output
    """

    def __init__(self):
        """
        Init a new instance of TemplateGenerator
        """
        self.__TEMPLATES_PATH = get_config_property("templates-path")
        self.__OUTPUT_PATH = get_config_property("output-path")
        return

    def generate_script(self, config_json):
        """
        Generate the AutoML specific scripts to execute the generated model
        ---
        Parameter:
        1. ML task
        """
        # Render Python script
        with open(os.path.join(self.__TEMPLATES_PATH, 'predict.ji')) as file:
            template = Template(file.read())
        script_file = open(os.path.join(self.__OUTPUT_PATH, config_json["session_id"], 'predict.py'), "w")
        script_file.write(template.render(task=config_json))

        # Render Requirement.txt
        with open(os.path.join(self.__TEMPLATES_PATH, 'requirements.ji')) as file:
            template = Template(file.read())
        script_file = open(os.path.join(self.__OUTPUT_PATH, config_json["session_id"], 'requirements.txt'), "w")
        script_file.write(template.render())
