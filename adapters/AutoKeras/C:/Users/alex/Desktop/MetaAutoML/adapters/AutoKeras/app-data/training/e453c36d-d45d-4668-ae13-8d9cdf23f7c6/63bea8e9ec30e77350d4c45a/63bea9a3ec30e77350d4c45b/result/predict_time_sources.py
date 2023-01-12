from enum import Enum, unique
import pandas as pd
import re



@unique
class SplitMethod(Enum):
    SPLIT_METHOD_RANDOM = 0
    SPLIT_METHOD_END = 1


def feature_preparation(X, features, datetime_format, is_prediction=False):
    target = ""
    is_target_found = False
    for column, dt in features:
        #During the prediction process no target column was read, so unnamed column names will be off by -1 index,
        #if they are located after the target column within the training set, their index must be adjusted
        if re.match(r"Column[0-9]+", column) and is_target_found == True and is_prediction == True:
            column_index = re.findall('[0-9]+', column)
            column_index = int(column_index[0])
            X.rename(columns={f"Column{column_index-1}": column}, inplace=True)

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
            is_target_found = True
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
            X[column] = X[column].astype('object')

        #Get target column
        if dt.get("role_selected", "") == ":target":
            target = column
            is_target_found = True

    if is_prediction == True:
        y = pd.Series()
    else:
        y = X[target]
        X.drop(target, axis=1, inplace=True)

    return X, y