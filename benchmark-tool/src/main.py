from dataset.dataset_configuration import DatasetConfiguration
from user.user import init_user
from dataset.dataset import upload_dataset
from config.config_validator import validate_config_values
from asyncio import run
from grpc_omaml.omaml_client import OmamlClient


async def main():
    configError = validate_config_values()
    if configError is not None:
        print(configError)
        return
    with OmamlClient() as client:
        userId = await init_user(client)

        # the dataset configuration is hardcoded for now.
        # Will be read from yaml in the near future.
        dataset_config = DatasetConfiguration(
            name_id="titanic",
            dataset_type=":tabular",
            file_location="../resources/titanic.csv",
        )
        await upload_dataset(client, userId, dataset_config)


if __name__ == "__main__":
    run(main())
