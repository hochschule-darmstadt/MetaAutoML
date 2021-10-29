import grpc
import Controller_pb2
import Controller_pb2_grpc

def printCLOptions():
    print("""
    help                        print all commands
    exit                        exit program
    get-session-status <id>     get the status of the session with the specified id
    ...
    """)


# loop and allow user to execute commands
def wait_for_commands(stub):
    while 1:
        command = input("").strip()
        if command == "help":
            printCLOptions()
        elif command == "exit":
            break
        elif command.startswith("get-session-status"):
            # TODO: the stub can contact the controller grpc server.
            #   But the program then crashes. Probably the wrong parameters are passed to GetSessionStatusRequest
            if command[-1].isdigit():
                id = str.encode(command[-1])
                request = Controller_pb2.GetSessionStatusRequest(id=id)
                response = stub.GetSessionStatus(request)
                print(f"{response}")
            else:
                print("invalid session id")
                continue
        else:
            print("invalid input")

def run():
    channel = grpc.insecure_channel('localhost:50051') # this requires the server in the controller to also start an insecure channel (not a secure one)
    stub = Controller_pb2_grpc.ControllerServiceStub(channel)

    wait_for_commands(stub)

run() # run script
