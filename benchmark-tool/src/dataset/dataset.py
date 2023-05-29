from uuid import UUID
from dataset.dataset_configuration import DatasetConfiguration
from grpc_omaml.omaml_client import OmamlClient


async def upload_dataset(
    client: OmamlClient, user_id: UUID, dataset: DatasetConfiguration
):
    """Uploads a dataset to omaml for the given user. For now the dataset is hardcoded.

    Args:
        client (OmamlClient): The omaml client to use
        user_id (UUID): The id of the user that the dataset is associated with
    """
    existing_dataset = await client.get_dataset_by_name(dataset.name_id, user_id)
    if existing_dataset is not None:
        return existing_dataset

    await client.create_dataset(
        dataset=dataset,
        user_id=user_id,
    )

    return await client.get_dataset_by_name(dataset.name_id, user_id)


async def configure_dataset(client: OmamlClient, user_id: UUID):
    pass
