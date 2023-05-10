from dataset.omaml_dataset_adapter import create_dataset, DatasetType


async def upload_dataset():
    await create_dataset(
        name="titanic",
        file_location="../resources/titanic_train.csv",
        dataset_type=DatasetType.TABULAR,
    )
