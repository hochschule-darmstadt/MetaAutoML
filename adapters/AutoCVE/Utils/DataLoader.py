from AdapterUtils import read_tabular_dataset_training_data


def data_loader(config):
    """
    Get exception message
    ---
    Parameter
    1. config: Job config
    ---
    Return job type specific dataset
    """

    train_data = None
    test_data = None

    if config["task"] == 1:
        train_data, test_data = read_tabular_dataset_training_data(config)
    elif config["task"] == 2:
        train_data, test_data = read_tabular_dataset_training_data(config)

    return train_data, test_data
