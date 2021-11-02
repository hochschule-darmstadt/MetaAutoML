import grpc
import Controller_pb2
import Controller_pb2_grpc
import sys


def printCLOptions():
    print("""
    help                        print all commands
    get-session-status <id>     get the status of the session with the specified id
    start-autml                 starts the automl with the titanic_train_1.csv dataset
    get-columns <dataset name>  returns all columns of a given dataset, e.g. for the dataset train.csv
    ...
    """)


def get_session_status(argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    if len(argv) == 1:
        id = argv[0]
        request = Controller_pb2.GetSessionStatusRequest(id=id)
        response = stub.GetSessionStatus(request)
        print(f"{response}")
    else:
        print("invalid session id")


def get_columns(argv, stub):
    if len(argv) == 1:
        dataset_name = argv[0]
        request = Controller_pb2.GetTabularDatasetColumnNamesRequest(datasetName=dataset_name)
        response = stub.GetTabularDatasetColumnNames(request)
        print(f"{response}")
    else:
        print("get-columns requires exactly one argument <column names>")


def start_automl(stub: Controller_pb2_grpc.ControllerServiceStub):
    tabular_config = Controller_pb2.AutoMLConfigurationTabularData(target="Survived")
    request = Controller_pb2.StartAutoMLprocessRequest(dataset="titanic_train_1.csv",
                                                       task=Controller_pb2.MACHINE_LEARNING_TASK_TABULAR_CLASSIFICATION,
                                                       tabularConfig=tabular_config)
    response = stub.StartAutoMLprocess(
        request)  # return (StartAutoMLprocessResponse {ControllerReturnCode result = 1;string sessionId = 2;})
    print(f"{response}")


def process_command(command: str, argv: list, stub: Controller_pb2_grpc.ControllerServiceStub):
    """
    @param command: the command like help, start-automl etc. that is telling the script what to do
    @param argv: the list of arguments passed along with that. e.g. get-session-status takes one argument <id>. But for instance help takes no arguments
    @param stub: the grpc-client stub which is used to process the commands
    @return: void
    """
    if command == "help":
        printCLOptions()
    elif command == "start-automl":
        start_automl(stub)

    elif command == "get-session-status":
        get_session_status(argv, stub)
    elif command == "get-columns":
        get_columns(argv, stub)
    else:
        print("invalid arguments")


def run():
    # TODO: change this to a secure channel
    channel = grpc.insecure_channel(
        'localhost:50051')  # this requires the server in the controller to also start an insecure channel (not a secure one)
    stub = Controller_pb2_grpc.ControllerServiceStub(channel)
    process_command(sys.argv[1], sys.argv[2:], stub)


run()  # run script
