from uuid import UUID
from dataset.dataset_type import DatasetType
from grpc_omaml.omaml_client import OmamlClient

__dataset_name = "titanic"


async def upload_dataset(client: OmamlClient, user_id: UUID):
    """Uploads a dataset to omaml for the given user. For now the dataset is hardcoded.

    Args:
        client (OmamlClient): The omaml client to use
        user_id (UUID): The id of the user that the dataset is associated with
    """
    existing_dataset = await client.get_dataset_by_name(__dataset_name, user_id)
    if existing_dataset is not None:
        return existing_dataset

    await client.create_dataset(
        name=__dataset_name,
        file_location="../resources/titanic_train.csv",
        dataset_type=DatasetType.TABULAR,
        user_id=user_id,
    )

    return await client.get_dataset_by_name(__dataset_name, user_id)
