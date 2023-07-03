from report.report import Report
from user.user import init_user
from dataset.dataset_configuration_reader import read_dataset_configuration
from dataset.dataset import configure_dataset, upload_dataset
from training.training import report_training_score, start_training, wait_for_training
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
        report = Report()
        # TODO: parallelize
        for dataset_config in dataset_configurations:
            try:
                datasetId = await upload_dataset(client, userId, dataset_config)
                print(f"Dataset {dataset_config.name_id} uploaded")
                await configure_dataset(client, userId, datasetId, dataset_config)
                trainingId = await start_training(
                    client, userId, datasetId, dataset_config
                )
                print(f"Training of dataset {dataset_config.name_id} started")
                await wait_for_training(client, userId, trainingId)
                await report_training_score(
                    client, userId, trainingId, report, dataset_config
                )
            except Exception as e:
                print(f"Training of dataset {dataset_config.name_id} failed: {e}")
        report.write_report()


if __name__ == "__main__":
    run(main())
