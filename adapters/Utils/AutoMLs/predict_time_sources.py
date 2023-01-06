from enum import Enum, unique
import pandas as pd



@unique
class SplitMethod(Enum):
    SPLIT_METHOD_RANDOM = 0
    SPLIT_METHOD_END = 1


def feature_preparation(X, features, datetime_format):
    targets = []
    for column, dt in features:

        #Check if column is to be droped either its role is ignore or index
        if dt.get("role_selected", "") == ":ignore" or dt.get("role_selected", "") == ":index":
            X.drop(column, axis=1, inplace=True)
            continue
        #Get column datatype
        datatype = dt.get("datatype_selected", "")
        if datatype == "":
            datatype = dt["datatype_detected"]

        if datatype == ":categorical":
            X[column] = X[column].astype('category')
        elif datatype == ":boolean":
            X[column] = X[column].astype('bool')
        elif datatype == ":integer":
            X[column] = X[column].astype('int')
        elif datatype == ":float":
            X[column] = X[column].astype('float')
        elif datatype == ":datetime":
            X[column] = pd.to_datetime(X[column], format=datetime_format)
        elif datatype == ":string":
            X[column] = X[column].astype('str')

        #Get target columns list
        if dt.get("role_selected", "") == ":target":
            targets.append(column)
    y = X[targets]
    X.drop(targets, axis=1, inplace=True)
    return X, y
