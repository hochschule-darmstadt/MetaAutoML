from user.user import init_user
from dataset.dataset_configuration_reader import read_dataset_configuration
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
        dataset_configurations = read_dataset_configuration()

        # TODO: parallelize
        for dataset_config in dataset_configurations:
            await upload_dataset(client, userId, dataset_config)


if __name__ == "__main__":
    run(main())
