import pyinstrument
from Container import Application
from dependency_injector.wiring import inject, Provide
from ControllerBGRPC import *
from DatasetManager import DatasetManager
from ModelManager import ModelManager
from OntologyManager import OntologyManager
import PredictionManager
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


USER_ID = "080a6480-bf52-4c30-9224-3f2b882fd5bb"
# USER_ID = "d6e5f211-b5a8-420e-a473-962a60a1e50d"

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
def get_trainings_metadata(
    get_trainings_request: "GetTrainingsMetadataRequest",
    training_manager: TrainingManager=Provide[Application.managers.training_manager]
) -> "GetTrainingsMetadataResponse":
    with Profiling():
        response = training_manager.get_trainings_metadata(get_trainings_request)

    print(response.trainings.count)

@inject
def get_training_metadata(
    get_training_request: "GetTrainingMetadataRequest",
    training_manager: TrainingManager=Provide[Application.managers.training_manager]
) -> "GetTrainingMetadataResponse":
    with Profiling():
        response = training_manager.get_training_metadata(get_training_request)

    print(response)

@inject
def get_training(
    get_training_request: "GetTrainingRequest",
    training_manager: TrainingManager=Provide[Application.managers.training_manager]
) -> "GetTrainingResponse":
    with Profiling():
        response = training_manager.get_training(get_training_request)

    training = response.training

    print(training)

@inject
def get_models(
    get_models_request: "GetModelsRequest",
    models_manager: ModelManager=Provide[Application.managers.model_manager]
) -> "GetModelsResponse":
    with Profiling():
        response = models_manager.get_models(get_models_request)

    print(len(response.models))

@inject
def get_predictions(
    get_predictions_request: "GetPredictionsRequest",
    predictions_manager: PredictionManager=Provide[Application.managers.prediction_manager]
) -> "GetPredictionsResponse":
    with Profiling():
        response = predictions_manager.get_predictions(get_predictions_request)

    print(len(response))

@inject
def get_dataset(
    get_dataset_request: "GetDatasetRequest",
    dataset_manager: DatasetManager=Provide[Application.managers.dataset_manager]
) -> "GetDatasetResponse":
    with Profiling():
        response = dataset_manager.get_dataset(get_dataset_request)

    print(response)


def main():
    # get_trainings(get_trainings_request=GetTrainingsMetadataRequest(user_id=USER_ID, pagination=True, page_number=1, page_size=10))
    # get_trainings(get_trainings_request=GetTrainingsMetadataRequest(user_id=USER_ID, pagination=True, page_number=1, page_size=25))
    # get_trainings(get_trainings_request=GetTrainingsMetadataRequest(user_id=USER_ID, pagination=True, page_number=1, page_size=50))
    # get_trainings(get_trainings_request=GetTrainingsMetadataRequest(user_id=USER_ID, pagination=True, page_number=1, page_size=100))
    # get_trainings(get_trainings_request=GetTrainingsMetadataRequest(user_id=USER_ID, pagination=True, page_number=1, page_size=200))
    # get_training_metadata(get_training_request=GetTrainingMetadataRequest(user_id=USER_ID, training_id="6722a7ab015fc5e2f632aaa7"))
    # get_training(get_training_request=GetTrainingRequest(user_id=USER_ID, training_id="6673475e6852060fb7c85502"))
    # get_predictions(get_predictions_request=GetPredictionsRequest(user_id=USER_ID, model_id="662253d39125e4518f9a68d3"))
    # get_models(get_models_request=GetModelsRequest(user_id=USER_ID, dataset_id="662254f59125e4518f9a68dd")) # airlines
    # get_models(get_models_request=GetModelsRequest(user_id=USER_ID, dataset_id="6667d4dc6852060fb7c853ed")) # led
    get_dataset(get_dataset_request=GetDatasetRequest(user_id=USER_ID, dataset_id="662254f59125e4518f9a68dd", short=True)) # airlines
    # get_dataset(get_dataset_request=GetDatasetRequest(user_id=USER_ID, dataset_id="662253c29125e4518f9a68d1")) # diabetes
    # get_dataset(get_dataset_request=GetDatasetRequest(user_id=USER_ID, dataset_id="6623ef3597eb741cec4b2569")) # KDDCup99


if __name__ == '__main__':
    """Python entry point setting up the dependency injection and starting main
    """
    application = Application()
    application.init_resources()
    application.wire(modules=["__main__"])
    main()
