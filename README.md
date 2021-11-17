# MetaAutoML-Adapter-Autosklearn

## ENVIRONTMENT VARIABLES
### PYTHONPATH
- must be set to all directories that include .py files
- is also set in the docker container, but there we prefix all paths with a "/", because inside the container the files are located in the root directory
- for local execution on linux PYTHONPATH=AutoMLs:templates:templates/output:Utils

### UNIX
- should be set, if running on a unix system. Things like file paths will be set accordingly

### PYTHON_ENV
- must be set to the desired python environment