import os
from typing import List
from uuid import UUID
from dataset.dataset_configuration import (
    DatasetConfiguration,
    DatasetColumnConfiguration,
    TrainingConfiguration,
)
from external.file_system import copy_file_to_folder
from grpc_omaml import (
    ControllerServiceStub,
    CreateDatasetRequest,
    CreateNewUserRequest,
    CreateTrainingRequest,
    GetDatasetRequest,
    GetDatasetsRequest,
    GetTrainingRequest,
    SetDatasetColumnSchemaConfigurationRequest,
    Training,
)
from grpclib.client import Channel
from config.config_accessor import (
    get_omaml_dataset_location,
    get_omaml_server_host,
    get_omaml_server_port,
)
from ssl import SSLContext, PROTOCOL_TLSv1_2, CERT_NONE
from config.config_accessor import get_disable_certificate_check
from grpc_omaml.omaml_error import OmamlError, TrainingFailedError
import grpc_omaml.omaml_typing_adapter as omaml_typing_adapter
from report.benchmark_result import TrainingResult


class OmamlClient:
    __grpc_client: ControllerServiceStub

    def __init__(self):
        # strangely enough, this is the type that the grpc library expects
        ssl: SSLContext | bool = True
        if get_disable_certificate_check():
            ssl = self.__get_ignore_certificate_config()

        channel = Channel(
            host=get_omaml_server_host(),
            port=get_omaml_server_port(),
            ssl=ssl,
        )
        self.__grpc_client = ControllerServiceStub(channel=channel)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        self.__grpc_client.channel.close()

    def __get_ignore_certificate_config(self):
        """Creates a ssl configuration that ignores the certificate.

        Returns:
            ssl configuration
        """
        ssl = SSLContext(PROTOCOL_TLSv1_2)
        ssl.check_hostname = False
        ssl.verify_mode = CERT_NONE
        return ssl

    async def create_user(self) -> UUID:
        """Creates a new user and returns its id.

        Raises:
            OmamlError: When an error occurs while creating the user

        Returns:
            UUID: The id of the user
        """
        try:
            response = await self.__grpc_client.create_new_user(
                create_new_user_request=CreateNewUserRequest()
            )
            return UUID(response.user_id)
        except Exception as e:
            raise OmamlError("Error while creating user: ") from e

    async def create_dataset(
        self, dataset: DatasetConfiguration, user_id: UUID
    ) -> None:
        """Uploads a dataset from a given path to omaml

        Args:
            name (str): The name of the dataset
            file_location (str): Path to the dataset file
            dataset_type (DatasetType): The type of the dataset (e.g. tabular)
            user_id (UUID): The id of the user that the dataset is associated with

        Raises:
            OmamlError: if the dataset could not be created
        """
        self.__file_upload(dataset.file_location, user_id)

        filename = os.path.basename(dataset.file_location)
        try:
            await self.__grpc_client.create_dataset(
                CreateDatasetRequest(
                    file_name=filename,
                    dataset_name=dataset.name_id,
                    dataset_type=dataset.dataset_type,
                    user_id=str(user_id),
                    encoding="utf-8",
                )
            )
        except Exception as e:
            raise OmamlError("Error while creating dataset: ") from e

    # currently this function mimics the behaviour of the frontend server when uploading files.
    def __file_upload(self, file_location: str, user_id: UUID):
        omaml_dataset_folder = get_omaml_dataset_location()
        copy_file_to_folder(
            file_location, os.path.join(omaml_dataset_folder, str(user_id), "uploads")
        )

    async def get_dataset_by_name(self, dataset_name: str, user_id: UUID) -> str | None:
        """Checks if a dataset with the given name exists for the given user

        Args:
            dataset_name (str): The name of the dataset
            user_id (UUID): The id of the user that the dataset is associated with

        Raises:
            OmamlError: if the datasets could not be fetched for the current user

        Returns:
            bool: The id of the dataset if it exists, None otherwise
        """
        try:
            result = await self.__grpc_client.get_datasets(
                GetDatasetsRequest(user_id=str(user_id))
            )

            # return single element from list that has the same name as the dataset_name
            return next(
                (
                    dataset.id
                    for dataset in result.datasets
                    if dataset.name == dataset_name
                ),
                None,
            )

        except Exception as e:
            raise OmamlError("Error while checking if dataset exists: ") from e

    async def set_dataset_column_schema(
        self,
        user_id: UUID,
        dataset_id: str,
        dataset_column: DatasetColumnConfiguration,
    ):
        """Sets the column schema for a dataset

        Args:
            user_id (UUID): The id of the user that the dataset is associated with
            dataset_id (str): The id of the dataset
            dataset_configuration (DatasetConfiguration): The dataset configuration
        """
        try:
            await self.__grpc_client.set_dataset_column_schema_configuration(
                SetDatasetColumnSchemaConfigurationRequest(
                    str(user_id),
                    dataset_id,
                    dataset_column.column_name,
                    dataset_column.column_type,
                    dataset_column.column_role,
                )
            )
        except Exception as e:
            raise OmamlError("Error while setting column schema: ") from e

    async def start_training(
        self, user_id: UUID, dataset_id: str, training_config: TrainingConfiguration
    ) -> str:
        """Starts the training of a dataset

        Args:
            user_id (UUID): The id of the user that the dataset is associated with
            dataset_id (str): The id of the dataset
            training_config (TrainingConfiguration): The training configuration

        Raises:
            OmamlError: if the training could not be started

        Returns:
            str: The id of the training
        """
        config = omaml_typing_adapter.training_configuration_to_omaml_config(
            training_config
        )
        try:
            return (
                await self.__grpc_client.create_training(
                    CreateTrainingRequest(str(user_id), dataset_id, config, "", False)
                )
            ).training_id
        except Exception as e:
            raise OmamlError("Error while starting training: ") from e

    async def verify_dataset_ready(self, user_id: UUID, dataset_id: str) -> bool:
        """Checks if a dataset is ready for training

        Args:
            user_id (UUID): The id of the user that the dataset is associated with
            dataset_id (str): The id of the dataset
        """
        try:
            dataset = (
                await self.__grpc_client.get_dataset(
                    GetDatasetRequest(str(user_id), dataset_id)
                )
            ).dataset
            return "number_of_columns" in dataset.analysis
        except Exception as e:
            raise OmamlError("Error while verifying dataset ready: ") from e

    async def get_training_completed(self, user_id: UUID, training_id: str) -> bool:
        """Checks if a training is completed

        Args:
            user_id (UUID): The id of the user that the dataset is associated with
            training_id (str): The id of the training

        Raises:
            OmamlError: if the training could not be fetched
            OmamlError: if the training failed

        Returns:
            bool: True if the training is completed, False otherwise
        """
        training: Training | None = None
        try:
            training = (
                await self.__grpc_client.get_training(
                    GetTrainingRequest(str(user_id), training_id)
                )
            ).training
            if training.status == "busy":
                return False
        except Exception as e:
            raise OmamlError("Error while checking if training completed: ") from e

        status_of_adapters = map(lambda m: m.status, training.models)
        if "failed" in status_of_adapters:
            raise TrainingFailedError("Training failed for at least one adapter")
        return True

    async def get_training_score(
        self, user_id: UUID, training_id: str
    ) -> List[TrainingResult]:
        """Gets the training score for a training

        Args:
            user_id (UUID): The id of the user that the dataset is associated with
            training_id (str): The id of the training

        Raises:
            OmamlError: if the training could not be fetched

        Returns:
            Dict[str, str]: AutoML to achieved score
        """
        try:
            training = (
                await self.__grpc_client.get_training(
                    GetTrainingRequest(str(user_id), training_id)
                )
            ).training
            return [
                TrainingResult(m.auto_ml_solution, m.test_score, m.status == "failed")
                for m in training.models
            ]
        except Exception as e:
            raise OmamlError("Error while getting training score: ") from e
