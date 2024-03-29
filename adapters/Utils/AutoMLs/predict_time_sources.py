from enum import Enum, unique
import pandas as pd
import re
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import OneHotEncoder

@unique
class SplitMethod(Enum):
    SPLIT_METHOD_RANDOM = 0
    SPLIT_METHOD_END = 1


def feature_preparation(X, features, datetime_format, is_prediction=False):
    target = ""
    is_target_found = False
    index_columns = []
    for column, dt in features:
        #During the prediction process no target column was read, so unnamed column names will be off by -1 index,
        #if they are located after the target column within the training set, their index must be adjusted
        if re.match(r"Column[0-9]+", column) and is_target_found == True and is_prediction == True:
            column_index = re.findall('[0-9]+', column)
            column_index = int(column_index[0])
            X.rename(columns={f"Column{column_index-1}": column}, inplace=True)

        #Check if column is to be droped, when its role is ignore
        if dt.get("role_selected", "") == ":ignore":
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
            X[column] = X[column].astype('int64')
        elif datatype == ":float":
            X[column] = X[column].astype('float64')
        elif datatype == ":datetime":
            X[column] = pd.to_datetime(X[column], format=datetime_format)
        elif datatype == ":string":
            X[column] = X[column].astype('object')

        #Get target column
        if dt.get("role_selected", "") == ":target":
            target = column
            is_target_found = True

        if dt.get("role_selected", "") == ":index":
            index_columns.append(column)

    #Handle target column appropriately depending on runtime
    if is_prediction == True:
        y = pd.Series()
    else:
        y = X[target]
        X.drop(target, axis=1, inplace=True)

    if len(index_columns) > 0:
        #Set index columns
        X.set_index(index_columns, inplace=True)

    return X, y


def string_feature_encoding(X, y, features):
    for column, dt in features:
        print("")
        if dt.get("preprocessing", "") == "":
            #Check preprocessing block exists, backwards compability
            dt["preprocessing"] = {}
        if dt["preprocessing"].get("encoding", "") == "":
            continue
        elif dt["preprocessing"]["encoding"]["type"] == "ordinal_encoding":
            ord_enc = OrdinalEncoder(dtype='int64')
            ord_enc.fit(dt["preprocessing"]["encoding"]["values"])
            X[column] = ord_enc.transform(X[[column]])
        elif dt["preprocessing"]["encoding"]["type"] == "one_hot_encoding":
            one_hot_enc = OneHotEncoder(dtype='int64', sparse_output=False).set_output(transform="pandas")
            one_hot_enc.fit(dt["preprocessing"]["encoding"]["values"])
            result = one_hot_enc.transform(X[[column]])
            for col in result.columns:
                result = result.rename(columns={ col : col.replace("x0", column)})
            X = pd.concat([X, result], axis=1).drop(columns=[column])
        else:
            continue

    return X, y