import pyinstrument
from Container import Application
from dependency_injector.wiring import inject, Provide
from ControllerBGRPC import *
from TrainingManager import TrainingManager

@inject
def get_training(
    get_trainings_request: "GetTrainingsMetadataRequest",
    training_manager: TrainingManager=Provide[Application.managers.training_manager]
):
    profiler = pyinstrument.Profiler()
    profiler.start()
    response = training_manager.get_trainings_metadata(get_trainings_request)
    profiler.stop()
    profiler.print()
    profiler.open_in_browser()
    print(response)

def main():
    get_training(get_trainings_request=GetTrainingsMetadataRequest(user_id="e763ec28-90ab-4621-9227-87c229be09fd", short=True))

if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    main()
