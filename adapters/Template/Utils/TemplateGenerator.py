from jinja2 import Template

import os
import sys

class TemplateGenerator(object):
    """
    Template generator to generate the custom AutoML output
    """
    def __init__(self):
        """
        Init a new instance of TemplateGenerator
        """
        return

    def GenerateScript(self, task):
        """
        Generate the AutoML specific scripts to execute the generated model
        ---
        Parameter:
        1. ML task
        """
        #Render Python script
        with open(os.path.join(os.path.dirname(sys.argv[0]), 'templates/PythonTemplate.ji')) as file:
            template = Template(file.read())
        script_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'templates/output/predict.py'), "w")
        script_file.write(template.render())

        #Render Requirement.txt
        with open(os.path.join(os.path.dirname(sys.argv[0]), 'templates/RequirementTemplate.ji')) as file:
            template = Template(file.read())
        script_file = open(os.path.join(os.path.dirname(sys.argv[0]), 'templates/output/requirements.txt'), "w")
        script_file.write(template.render())
