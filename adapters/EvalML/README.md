# MetaAutoML-Adapter-FLAML

This repository implements the MetaAutoML-Adapter for the AutoML library EvalML (https://github.com/microsoft/FLAML).

## ENVIRONTMENT VARIABLES
### PYTHONPATH
- must be set to all directories that include .py files
- is also set in the docker container, but there we prefix all paths with a "/", because inside the container the files are located in the root directory
- for local execution on linux you can use the configuration as it is used in the Dockerfile

### PYTHON_ENV
- must be set to the desired python environment

### GRPC_SERVER_PORT
- must be set to the port where the adapter is listening for calls from the controller, currently 50062

### Development tips
- EvalML uses Woodwork (https://woodwork.alteryx.com/en/stable/ , a library from alteryx) in order to help with data typing of 2-dimensional tabular data structures.
The Woodwork schema will be auto generated from dataframe, data series, etc.. With different numbers of data rows, the generated schema could also be diffrent (inconsistent).
Therefore in oder to make prediction, wood work schema from training and testing data set have to be identical. We can make it either using split data function from evalml
or init the testing set with schema of training set (see the explain model function).
- For time Series tasks, we must persist time(or date, datetime,..) column by reset index. Test data sete also have to include target column.
- For local debugging in Windows, set the desire Test file in lauch.json and debbug.
