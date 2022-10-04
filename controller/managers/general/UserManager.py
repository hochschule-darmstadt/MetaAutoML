import threading
from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import logging, os, uuid
from CsvManager import CsvManager
from LongitudinalDataManager import LongitudinalDataManager

class UserManager:

    def __init__(self, data_storage: DataStorage) -> None:
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('UserManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        
    def create_new_user(
        self, create_new_user_request: "CreateNewUserRequest"
    ) -> "CreateNewUserResponse":
        """
        Create a new user
        ---
        Parameter
        1. grpc request object, empty
        ---
        Return a new user identifier
        The result is a CreateNewUserResponse object describing one dataset or a GRPC error if ressource ALREADY_EXISTS
        """
        user_identifier = str(uuid.uuid4())
        self.__log.debug(f"create_new_user: trying to create a new user {user_identifier}")
        if self.__data_storage.check_if_user_exists(user_identifier) == True:
            self.__log.error(f"create_new_user: user already exists {user_identifier}")
            raise grpclib.GRPCError(grpclib.Status.ALREADY_EXISTS, f"error while creating new user, uuid already exists")
        else:
            self.__log.debug(f"create_new_user: copying default dataset for a new user {user_identifier}")
            CsvManager.copy_default_dataset(user_identifier)
            self.__data_storage.create_dataset(user_identifier, "titanic_train.csv", ":tabular", "Titanic")
            return CreateNewUserResponse(user_identifier)

    def get_home_overview_information(
        self, get_home_overview_information_request: "GetHomeOverviewInformationRequest"
    ) -> "GetHomeOverviewInformationResponse":
        """
        Get information for home overview page of a user
        ---
        Parameter
        1. grpc request object, containing the user identifier
        ---
        The result is a GetHomeOverviewInformationResponse object containing the infos for the home overview
        """
        response = GetHomeOverviewInformationResponse()
        self.__log.debug(f"get_home_overview_information: retriving users home overview page infos {get_home_overview_information_request.user_identifier}")
        response.dataset_amount = len(self.__data_storage.get_datasets(get_home_overview_information_request.user_identifier))
        self.__log.debug(f"get_home_overview_information: total dataset amount {response.dataset_amount}")
        response.model_amount = len(self.__data_storage.get_models(get_home_overview_information_request.user_identifier))
        self.__log.debug(f"get_home_overview_information: total model amount {response.model_amount}")
        total_trainings = self.__data_storage.get_trainings(get_home_overview_information_request.user_identifier)
        response.training_amount = len(total_trainings)
        self.__log.debug(f"get_home_overview_information: total training amount {response.training_amount}")
        response.running_training_amount = len([t for t in total_trainings if t["status"] == "busy"])
        self.__log.debug(f"get_home_overview_information: total running training amount {response.running_training_amount}")
        return response