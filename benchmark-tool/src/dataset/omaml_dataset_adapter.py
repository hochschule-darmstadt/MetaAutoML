import os
from uuid import UUID
from external.file_system import move_file_to_folder, get_filename_from_path
from dataset.dataset_type import DatasetType, type_to_omaml_id
from config.config_accessor import get_omaml_dataset_location
from grpc_omaml.client_factory import create_omaml_client
from grpc_omaml import CreateDatasetRequest
from grpc_omaml.omaml_error import OmamlError


async def create_dataset(
    name: str, file_location: str, dataset_type: DatasetType, user_id: UUID
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
    __file_upload(file_location, user_id)

    client = create_omaml_client()
    filename = get_filename_from_path(file_location)

    try:
        await client.create_dataset(
            CreateDatasetRequest(
                file_name=filename,
                dataset_name=name,
                dataset_type=type_to_omaml_id(dataset_type),
                user_id=str(user_id),
                encoding="utf-8",
            )
        )
    except Exception as e:
        raise OmamlError("Error while creating dataset: ") from e


# currently this function mimics the behaviour of the frontend server when uploading files.
def __file_upload(file_location: str, user_id: UUID):
    omaml_dataset_folder = get_omaml_dataset_location()
    move_file_to_folder(
        file_location, os.path.join(omaml_dataset_folder, str(user_id), "uploads")
    )


# todo: function that returns whether a dataset already exists
