# Repository for the Controller component of OMA-ML

This repository contains the controller segment of OMA-ML:

![](https://github.com/hochschule-darmstadt/MetaAutoML-Controller/blob/main/docs/images/controller-overview.png)

## Installation

Clone the repository and set up a local project using the requirements.txt for an local python enviromnent.

## Project Overview

- `Controller_pb2_grpc.py` is the RPC interface for the RPC server running in the controller, which is accessible for the frontend.
- `Adapter_pb2_grpc.py` is the RPC interface running in the adapters, which is then called by the controller.

## ENV Variables:
- `PYTHONPATH` must be set to all directories that contain python source files (separated by a colon on unix)
- `RUNTIME` must be set to 1 if running in docker
- `PYTHONUNBUFFERED=1` should always be set
- `<AUTOML_NAME>_SERVICE_HOST` should be set to the ip address of the respective Adapter
- `<AUTOML_NAME>_SERVICE_PORT` should be set to the port on which the respective Adapter is listening to connections from the controller

it is recommended to start the whole project using the docker-compose.yml file in the meta repository, because there all environment variables are preconfigured

PYTHON_ENV=python;MLJAR_SERVICE_HOST=localhost;MLJAR_SERVICE_PORT=50059;AUTOCVE_SERVICE_HOST=localhost;AUTOCVE_SERVICE_PORT=50060;FLAML_SERVICE_HOST=localhost;FLAML_SERVICE_PORT=50056;SKLEARN_SERVICE_HOST=localhost;SKLEARN_SERVICE_PORT=50058;PYTORCH_SERVICE_HOST=localhost;PYTORCH_SERVICE_PORT=50057;AUTOGLUON_SERVICE_HOST=localhost;AUTOGLUON_SERVICE_PORT=50054;AUTOKERAS_SERVICE_HOST=localhost;AUTOKERAS_SERVICE_PORT=50053