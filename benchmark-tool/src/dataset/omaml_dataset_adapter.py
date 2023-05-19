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


def __file_upload(file_location: str):
    move_file_to_folder(file_location, get_omaml_dataset_location())


# todo: function that returns whether a dataset already exists
