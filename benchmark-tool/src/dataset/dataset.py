from uuid import UUID
from dataset.dataset_type import DatasetType
from dataset.omaml_dataset_adapter import create_dataset


async def upload_dataset(user_id: UUID):
    """Uploads a dataset to omaml for the given user. For now the dataset is hardcoded.

    Args:
        user_id (UUID): The id of the user that the dataset is associated with
    """
    await create_dataset(
        name="titanic",
        file_location="../resources/titanic_train.csv",
        dataset_type=DatasetType.TABULAR,
        user_id=user_id,
    )
