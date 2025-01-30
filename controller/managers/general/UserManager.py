import threading
from DataStorage import DataStorage
from ControllerBGRPC import *
from DataStorage import DataStorage
import logging, os, uuid
from CsvManager import CsvManager
from DataSetAnalysisManager import DataSetAnalysisManager
from ThreadLock import ThreadLock

from concurrent.futures import ThreadPoolExecutor
import asyncio

class UserManager:
    """The UserManager provides all functionality related to a User and not a specific data schema objects
    """

    def __init__(self, data_storage: DataStorage, dataset_analysis_lock: ThreadLock) -> None:
        """Initialize a new UserManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
            dataset_analysis_lock (ThreadLock): The dataset analysis lock instance to protect from multiple thread using critical parts of the DatasetAnalysisManager
        """
        self.__data_storage: DataStorage = data_storage
        self.__dataset_analysis_lock = dataset_analysis_lock
        self.__log = logging.getLogger('UserManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))

    async def run_dataset_analysis(self, dataset_id, user_id):
        dataset_analysis = DataSetAnalysisManager(dataset_id, user_id, self.__data_storage)
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, dataset_analysis.run_analysis)

    def create_new_user(
        self, create_new_user_request: "CreateNewUserRequest"
    ) -> "CreateNewUserResponse":
        """Create a new OMA-ML user, by generating a unique UUID used to identify the users ressources inside MongoDB. This UUID must be linked/persisted inside the frontend

        Args:
            create_new_user_request (CreateNewUserRequest): The empty GRPC request message

        Raises:
            grpclib.GRPCError: grpclib.Status.ALREADY_EXISTS, raised if the generated UUID already exists

        Returns:
            CreateNewUserResponse: The GRPC response message holding the new user UUID
        """
        user_id = str(uuid.uuid4())
        self.__log.debug(f"create_new_user: trying to create a new user {user_id}")
        if self.__data_storage.check_if_user_exists(user_id) == True:
            self.__log.error(f"create_new_user: user already exists {user_id}")
            raise grpclib.GRPCError(grpclib.Status.ALREADY_EXISTS, f"error while creating new user, uuid already exists")
        else:
            self.__log.debug(f"create_new_user: copying default dataset for a new user {user_id}")
            CsvManager.copy_default_dataset(user_id)
            dataset_id: str = self.__data_storage.create_dataset(user_id, "titanic_train.csv", ":tabular", "Titanic", "utf-8")
            self.__log.debug("create_dataset: executing dataset analysis...")
            asyncio.create_task(self.run_dataset_analysis(dataset_id, user_id))
            return CreateNewUserResponse(user_id)

    def get_home_overview_information(
        self, get_home_overview_information_request: "GetHomeOverviewInformationRequest"
    ) -> "GetHomeOverviewInformationResponse":
        """Get information for the home overview page of a user (# datasets, trainings, models, active trainings)

        Args:
            get_home_overview_information_request (GetHomeOverviewInformationRequest): GRPC message holding the user id

        Returns:
            GetHomeOverviewInformationResponse: The GRPC response message holding the infos for the home overview
        """
        return self.__data_storage.get_home_overview_information(get_home_overview_information_request.user_id)
