from uuid import UUID
from dataset.dataset_configuration import DatasetConfiguration
from grpc_omaml.omaml_client import OmamlClient
from config.config_accessor import get_dataset_analysis_timeout_seconds
from asyncio import sleep


async def upload_dataset(
    client: OmamlClient, user_id: UUID, dataset: DatasetConfiguration
) -> str:
    """Uploads a dataset to omaml for the given user. For now the dataset is hardcoded.

    Args:
        client (OmamlClient): The omaml client to use
        user_id (UUID): The id of the user that the dataset is associated with

    Returns:
        str: The id of the uploaded dataset
    """
    existing_dataset = await client.get_dataset_by_name(dataset.name_id, user_id)
    if existing_dataset is not None:
        return existing_dataset

    await client.create_dataset(
        dataset=dataset,
        user_id=user_id,
    )

    datasetId = await client.get_dataset_by_name(dataset.name_id, user_id)
    if datasetId is None:
        raise Exception("Dataset was not uploaded correctly")

    print("start waiting for dataset to be ready")
    timeout = get_dataset_analysis_timeout_seconds() * 10
    for _ in range(timeout):
        if await client.verify_dataset_ready(user_id, datasetId):
            print("dataset is ready")
            break
        await sleep(0.1)
    return datasetId


async def configure_dataset(
    client: OmamlClient, user_id: UUID, dataset_id: str, dataset: DatasetConfiguration
):
    """Configures a dataset in omaml for the given user

    Args:
        client (OmamlClient): The omaml client to use
        user_id (UUID): The id of the user that the dataset is associated with
        dataset_id (str): The id of the dataset
        dataset_configuration (DatasetConfiguration): The dataset configuration
    """
    for column in dataset.columns:
        await client.set_dataset_column_schema(
            user_id=user_id,
            dataset_id=dataset_id,
            dataset_column=column,
        )
