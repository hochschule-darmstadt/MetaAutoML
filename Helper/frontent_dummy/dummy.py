import grpc
import Controller_pb2
import Controller_pb2_grpc
import sys
import pickle

def print_cl_options():
    print("""
    help                        print all commands
    get-session-status <id>     get the status of the session with the specified id
    start-automl <dataset name> <target> <task>
                                starts the automl
                                the parameters have the following defaults for a quick test:
                                <dataset>="titanic_train_1.csv"
                                <target>="Survived"
                                <task>="classification"
    get-columns <dataset name>  returns all columns of a given dataset,
                                e.g. if you want to get the column names of the dataset train.csv, then call
                                get-columns train.csv
    get-tasks <dataset name>    returns all tasks for a given dataset,
                                e.g. if you want to the tasks for the dataset train.csv, then call
                                get-tasks train.csv
    get-datasets                returns all datasets as json
    get-dataset                 returns the information about the specified dataset as json,
                                e.g. call get-dataset train.csv to receive information about the train.csv dataset
    get-sessions                returns all active sessions
    get-automl-model <id> <automl name>       
                                returns the generated model of the specified sessionId as a .zip file
    upload-dataset <file name>  uploads the specified file as a dataset
    """)

def get_automl_model(argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    if len(argv) == 2:
        session_id = argv[0]
        name = argv[1]
        request = Controller_pb2.GetAutoMlModelRequest(sessionId=session_id, autoMl=name)
        response = stub.GetAutoMlModel(request)
        print(f"saving file {response.name}")
        with open(response.name, 'wb') as file:
            pickle.dump(response.file, file)
    else:
        print("get_automl_model requires exactly one argument <session id>")

def upload_dataset(argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    if len(argv) == 1:
        filename = argv[0]
        request = Controller_pb2.UploadDatasetFileRequest(name=filename)
        with open(filename, "rb") as file:
            request.content = file.read()
        response = stub.UploadDatasetFile(request)
        print(f"{response}")
    else:
        print("upload_dataset requires exactly one argument <file name>")

def get_session_status(argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    if len(argv) == 1:
        id = argv[0]
        request = Controller_pb2.GetSessionStatusRequest(id=id)
        response = stub.GetSessionStatus(request)
        print(f"{response}")
    else:
        print("invalid session id")


def get_sessions(argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    if len(argv) > 0:
        print("No args necessary for sessions request. Args will be ignored.")
    request = Controller_pb2.GetSessionsRequest()
    response = stub.GetSessions(request)
    print(f"{response}")


def get_columns(argv, stub):
    if len(argv) == 1:
        dataset_name = argv[0]
        request = Controller_pb2.GetTabularDatasetColumnNamesRequest(datasetName=dataset_name)
        response = stub.GetTabularDatasetColumnNames(request)
        print(f"{response}")
    else:
        print("get-columns requires exactly one argument <dataset names>")


def get_tasks(argv, stub):
    if len(argv) == 1:
        dataset_name = argv[0]
        request = Controller_pb2.GetTasksRequest(datasetName=dataset_name)
        response = stub.GetTasks(request)
        print(f"{response}")
    else:
        print("get-tasks requires exactly one argument <dataset names>")


def get_datasets(stub):
    # GetDatasetsRequest actually has a parameter called 'type'. But this parameter is not yet used in the controller.
    request = Controller_pb2.GetDatasetsRequest()
    response = stub.GetDatasets(request)
    print(f"{response}")


def start_automl(argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    """"
    @param stub: the grpc-client stub which is used to process the commands
    @param argv: parameter list as follows:
        argv[0] = <dataset name>        default = "titanic_train_1.csv"
        argv[1] = <target column>       default = "Survived"
    """

    if len(argv) < 0 or len(argv) > 3:
        print("start_automl requires 0 to 3 arguments: <dataset name>='titanic_train_1.csv' "
              "<target column>='Survived' <task>='classification'")
        return

    dataset_name = "titanic_train_1.csv"
    target_column = "Survived"
    task = Controller_pb2.MACHINE_LEARNING_TASK_TABULAR_CLASSIFICATION

    if len(argv) > 0:
        dataset_name = argv[0]
    if len(argv) > 1:
        target_column = argv[1]
    if len(argv) > 2:
        if argv[2] == "regression":
            task = Controller_pb2.MACHINE_LEARNING_TASK_TABULAR_REGRESSION
        elif argv[2] == "classification":
            task = Controller_pb2.MACHINE_LEARNING_TASK_TABULAR_CLASSIFICATION
        else:
            print("task has to be 'regression' or 'classification'")
            return

    tabular_config = Controller_pb2.AutoMLConfigurationTabularData(target=target_column)

    request = Controller_pb2.StartAutoMLprocessRequest(dataset=dataset_name,
                                                       task=task,
                                                       tabularConfig=tabular_config)
    response = stub.StartAutoMLprocess(
        request)  # return (StartAutoMLprocessResponse {ControllerReturnCode result = 1;string sessionId = 2;})
    print(f"{response}")


def get_dataset(argv, stub):
    if len(argv) == 1:
        request = Controller_pb2.GetDatasetRequest(name=argv[0])
        response = stub.GetDatasets(request)
        print(f"{response}")
    else:
        print("get-dataset requires exactly one argument <dataset name>")


def process_command(command: str, argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    """
    @param command: the command like help, start-automl etc. that is telling the script what to do
    @param argv: the list of arguments passed along with that. e.g. get-session-status takes one argument <id>. But for instance help takes no arguments
    @param stub: the grpc-client stub which is used to process the commands
    @return: void
    """
    if command == "help":
        print_cl_options()
    elif command == "start-automl":
        start_automl(argv, stub)
    elif command == "get-session-status":
        get_session_status(argv, stub)
    elif command == "get-sessions":
        get_sessions(argv, stub)
    elif command == "get-columns":
        get_columns(argv, stub)
    elif command == "get-tasks":
        get_tasks(argv, stub)
    elif command == "get-datasets":
        get_datasets(stub)
    elif command == "get-dataset":
        get_dataset(argv, stub)
    elif command == "get-automl-model":
        get_automl_model(argv, stub)
    elif command == "upload-dataset":
        upload_dataset(argv, stub)
    else:
        print("invalid arguments")


def run():
    with open('root.crt', 'rb') as f:
        creds = grpc.ssl_channel_credentials(f.read())
    channel = grpc.secure_channel('localhost:5001', creds)
    #channel = grpc.insecure_channel('localhost:50051')
    stub = Controller_pb2_grpc.ControllerServiceStub(channel)
    process_command(sys.argv[1], sys.argv[2:], stub)


run()  # run script
