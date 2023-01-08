from enum import Enum, unique
import pandas as pd



@unique
class SplitMethod(Enum):
    SPLIT_METHOD_RANDOM = 0
    SPLIT_METHOD_END = 1


def feature_preparation(X, features, datetime_format, is_prediction=False):
    target = ""
    for column, dt in features:

        #Check if column is to be droped either its role is ignore or index
        if dt.get("role_selected", "") == ":ignore" or dt.get("role_selected", "") == ":index":
            X.drop(column, axis=1, inplace=True)
            continue
        #Get column datatype
        datatype = dt.get("datatype_selected", "")
        if datatype == "":
            datatype = dt["datatype_detected"]

        #during predicitons we dont have a target column and must avoid casting it
        if dt.get("role_selected", "") == ":target" and is_prediction == True:
            continue

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

        #Get target column
        if dt.get("role_selected", "") == ":target":
            target = column

    if is_prediction == True:
        y = pd.Series()
    else:
        y = X[target]
        X.drop(target, axis=1, inplace=True)

    return X, y
