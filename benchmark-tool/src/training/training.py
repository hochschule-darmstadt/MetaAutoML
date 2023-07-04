from uuid import UUID
from dataset.dataset_configuration import DatasetConfiguration
from grpc_omaml.omaml_client import OmamlClient
from external.sleeper import sleep
from report.report import Report
from report.benchmark_result import BenchmarkResult


def start_training(
    client: OmamlClient,
    user_id: UUID,
    dataset_id: str,
    dataset_config: DatasetConfiguration,
):
    """Starts a training for the given dataset

    Args:
        client (OmamlClient): The omaml client to use
        user_id (UUID): The id of the user that the dataset is associated with
        dataset_id (str): The id of the dataset
        dataset_config (DatasetConfiguration): The dataset configuration

    Returns:
        str: The id of the training
    """
    return client.start_training(user_id, dataset_id, dataset_config.training)


async def wait_for_training(client: OmamlClient, user_id: UUID, training_id: str):
    """Waits for the training to finish

    Args:
        client (OmamlClient): The omaml client to use
        user_id (UUID): The id of the user that the dataset is associated with
        training_id (str): The id of the training
    """
    while True:
        if await client.get_training_completed(user_id, training_id):
            break
        await sleep(60)


async def report_training_score(
    client: OmamlClient,
    user_id: UUID,
    training_id: str,
    report: Report,
    dataset: DatasetConfiguration,
):
    """Gets the score of the training

    Args:
        client (OmamlClient): The omaml client to use
        user_id (UUID): The id of the user that the dataset is associated with
        training_id (str): The id of the training
        report (Report): The report to write the score to
        dataset (DatasetConfiguration): The dataset configuration
    """
    auto_ml_to_score = await client.get_training_score(user_id, training_id)
    for training_result in auto_ml_to_score:
        report.add_benchmark_result(
            BenchmarkResult(
                dataset_name=dataset.name_id,
                auto_ml_solution=training_result.auto_ml_solution,
                target_metric=dataset.training.metric,
                achieved_score=training_result.achieved_score
                if not training_result.is_failed
                else "failed",
            )
        )
