import sys
import pickle
import json
from predict_time_sources import feature_preparation, DataType, SplitMethod

import pandas as pd
import numpy as np
from flaml import AutoML

if __name__ == '__main__':
    filepath = sys.argv[1]
    config_path = sys.argv[2]

    with open(config_path) as file:
        config_json = json.load(file)

    target = config_json["tabular_configuration"]["target"]["target"]
    features = config_json["tabular_configuration"]["features"].items()
    X = pd.read_csv(filepath).drop(target, axis=1, errors='ignore')

    # split training set
    if SplitMethod.SPLIT_METHOD_RANDOM == config_json["test_configuration"]["method"]:
        X = X.sample(random_state=config_json["test_configuration"]["random_state"], frac=1)
    else:
        X = X.iloc[int(X.shape[0] * config_json["test_configuration"]["split_ratio"]):]

    X = feature_preparation(X, features)

    with open(sys.path[0] + '/model_flaml.p', 'rb') as file:
        automl2 = pickle.load(file)

    predicted_y = automl2.predict(X)
    predicted_y = np.reshape(predicted_y, (-1, 1))
    pd.DataFrame(data=predicted_y, columns=["predicted"]).to_csv(sys.path[0] + "/predictions.csv")