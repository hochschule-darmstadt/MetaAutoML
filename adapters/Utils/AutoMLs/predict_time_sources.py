from enum import Enum, unique
import pandas as pd

@unique
class DataType(Enum):
    DATATYPE_UNKNOW = 0
    DATATYPE_STRING = 1
    DATATYPE_INT = 2
    DATATYPE_FLOAT = 3
    DATATYPE_CATEGORY = 4
    DATATYPE_BOOLEAN = 5
    DATATYPE_DATETIME = 6
    DATATYPE_IGNORE = 7


@unique
class SplitMethod(Enum):
    SPLIT_METHOD_RANDOM = 0
    SPLIT_METHOD_END = 1


def feature_preparation(X, features):
    for column, dt in features:
        if DataType(dt) is DataType.DATATYPE_IGNORE:
            X.drop(column, axis=1, inplace=True)
        elif DataType(dt) is DataType.DATATYPE_CATEGORY:
            X[column] = X[column].astype('category')
        elif DataType(dt) is DataType.DATATYPE_BOOLEAN:
            X[column] = X[column].astype('bool')
        elif DataType(dt) is DataType.DATATYPE_INT:
            X[column] = X[column].astype('int')
        elif DataType(dt) is DataType.DATATYPE_FLOAT:
            X[column] = X[column].astype('float')
    return X

def encode_category_columns(X, json_configuration):
    if "encoded_columns" in json_configuration["dataset_configuration"]:
        encoded_columns = json_configuration["dataset_configuration"]["encoded_columns"]
        X = pd.get_dummies(data=X, columns=encoded_columns)

        #create list of final columns
        final_columns = []
        final_columns.extend(json_configuration["dataset_configuration"]["column_datatypes"].keys())
        for key in encoded_columns:
            final_columns.extend(encoded_columns[key])
            final_columns.remove(key)

        #initialize new columns that are created due to one hot encoding with 0
        for column_name in final_columns:
            if column_name not in X:
                X[column_name] = 0

        #drop columns that were not in the training data
        X = X[X.columns.intersection(final_columns)]
    return X