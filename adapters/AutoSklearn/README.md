# MetaAutoML-Adapter-Autosklearn

## ENVIRONTMENT VARIABLES
### PYTHONPATH
- must be set to all directories that include .py files
- is also set in the docker container, but there we prefix all paths with a "/", because inside the container the files are located in the root directory
- for local execution on linux you can use the configuration as it is used in the Dockerfile

### PYTHON_ENV
- must be set to the desired python environment

### GRPC_SERVER_PORT
- must be set to the automl listens on to connections from controller