import pyinstrument
from Container import Application
from dependency_injector.wiring import inject, Provide
from ControllerBGRPC import *
from DatasetManager import DatasetManager
from OntologyManager import OntologyManager
from UserManager import UserManager
from TrainingManager import TrainingManager

class Profiling:
    def __init__(self):
        self.profiler = pyinstrument.Profiler()

    def __enter__(self):
        self.profiler.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.profiler.stop()
        self.profiler.print()
        self.profiler.open_in_browser()


USER_ID = "0ba2fb0e-6eec-4225-a95f-7d5900afa56f"

@inject
def get_home_overview_information(
    get_home_overview_information_request: "GetHomeOverviewInformationRequest",
    user_manager: UserManager=Provide[Application.managers.user_manager]
):
    with Profiling():
        response = user_manager.get_home_overview_information(get_home_overview_information_request)

    print(response)

@inject
def get_search_relevant_data(
    ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
) -> "GetSearchRelevantDataResponse":
    with Profiling():
        response = ontology_manager.get_search_relevant_data()

    print(response)

@inject
def get_dataset_types(
    ontology_manager: OntologyManager=Provide[Application.ressources.ontology_manager]
) -> "GetDatasetTypesResponse":
    with Profiling():
        response = ontology_manager.get_dataset_types()

    print(response)

@inject
def get_datasets(
    get_datasets_request: "GetDatasetsRequest",
    dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
) -> "GetDatasetsResponse":
    with Profiling():
        response = dataset_manager.get_datasets(get_datasets_request)

    print(response)

@inject
def get_trainings(
    get_trainings_request: "GetTrainingsRequest",
    training_manager: TrainingManager=Provide[Application.managers.training_manager]
) -> "GetTrainingsResponse":
    with Profiling():
        response = training_manager.get_trainings(get_trainings_request)

    print(response.trainings.count)

def main():
    get_trainings(get_trainings_request=GetTrainingsRequest(user_id=USER_ID, pagination=True, page_number=1))

if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    main()
