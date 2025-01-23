import pyinstrument
from Container import Application
from dependency_injector.wiring import inject, Provide
from ControllerBGRPC import *
from TrainingManager import TrainingManager

@inject
def get_training(
    get_trainings_request: "GetTrainingsRequest",
    training_manager: TrainingManager=Provide[Application.managers.training_manager]
):
    profiler = pyinstrument.Profiler()
    profiler.start()
    response = training_manager.get_trainings(get_trainings_request)
    profiler.stop()
    profiler.print()
    profiler.open_in_browser()
    print(response)

def main():
    get_training(get_trainings_request=GetTrainingsRequest(user_id="28a5e888-82db-4413-a8e3-6d78ea33bdc3", short=True, pagination=True, page_number=1, page_size=100))

if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    main()
