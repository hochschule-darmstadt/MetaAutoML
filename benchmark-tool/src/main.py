from user.user import init_user
from dataset.dataset_configuration_reader import read_dataset_configuration
from dataset.dataset import configure_dataset, upload_dataset
from training.training import start_training
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
        print(f"User id: {userId}")
        dataset_configurations = read_dataset_configuration()

        # TODO: parallelize
        for dataset_config in dataset_configurations:
            datasetId = await upload_dataset(client, userId, dataset_config)
            await configure_dataset(client, userId, datasetId, dataset_config)
            await start_training(client, userId, datasetId, dataset_config)


if __name__ == "__main__":
    run(main())
