from uuid import UUID
from dataset.dataset_configuration import DatasetConfiguration
from grpc_omaml.omaml_client import OmamlClient


async def start_training(
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
    """
    await client.start_training(user_id, dataset_id, dataset_config.training)
