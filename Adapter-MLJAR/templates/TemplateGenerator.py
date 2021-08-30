from jinja2 import Template

import os
import sys

class TemplateGenerator(object):
    def __init__(self):
        return

    def GenerateScript(self):
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
