import pyinstrument
from Container import Application
from dependency_injector.wiring import inject, Provide
from ControllerBGRPC import *
from DatasetManager import DatasetManager
from OntologyManager import OntologyManager
from UserManager import UserManager

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
def get_datasets(
    get_datasets_request: "GetDatasetsRequest",
    dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
) -> "GetDatasetsResponse":
    with Profiling():
        response = dataset_manager.get_datasets(get_datasets_request)

    print(response)

def main():
    get_home_overview_information(get_home_overview_information_request=GetHomeOverviewInformationRequest(user_id="d6e5f211-b5a8-420e-a473-962a60a1e50d"))
    get_search_relevant_data()
    get_datasets(get_datasets_request=GetDatasetsRequest(user_id="d6e5f211-b5a8-420e-a473-962a60a1e50d", pagination=True, page_number=1))

if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    main()
