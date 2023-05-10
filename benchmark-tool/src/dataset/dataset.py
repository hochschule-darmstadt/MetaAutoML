from dataset.dataset_type import DatasetType
from dataset.omaml_dataset_adapter import create_dataset


async def upload_dataset():
    await create_dataset(
        name="titanic",
        file_location="../resources/titanic_train.csv",
        dataset_type=DatasetType.TABULAR,
    )
