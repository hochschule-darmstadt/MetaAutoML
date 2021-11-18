import pickle
import pandas as pd
import numpy as np
import sys

if __name__ == '__main__':
    filepath = sys.argv[1]

    X = pd.read_csv(filepath, quotechar='"', skipinitialspace=True)
    # convert all object columns to categories, because autosklearn only supports numerical, bool and categorical features
    X[X.select_dtypes(['object']).columns] = X.select_dtypes(['object']) \
        .apply(lambda x: x.astype('category'))

    with open('autosklearn-model.p', 'rb') as file:
        automl = pickle.load(file)

    predicted_y = automl.predict(X)
    predicted_y = np.reshape(predicted_y, (-1, 1))
    print(predicted_y)