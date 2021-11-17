import os
from autogluon.tabular import TabularDataset, TabularPredictor

class StructuredDataAutoML(object):
    """
    Implementation of the AutoML functionality fo structured data a.k.a. tabular data
    """
    def __init__(self, configuration: dict):
        """
        Init a new instance of StructuredDataAutoML
        ---
        Parameter:
        1. Configuration JSON of type dictionary
        """
        self.__configuration = configuration
        return

    def __read_training_data(self):
        """
        Read the training dataset from disk
		In case of AutoGluon only provide the training file path
        """
        self.__training_data_path = os.path.join(self.__configuration["file_location"], self.__configuration["file_name"])
        #self.__X = df.drop(self.__configuration["configuration"]["target"], axis=1)
        #self.__y = df[self.__configuration["configuration"]["target"]]

    # def __export_model(self, model):
    #     """
    #     Export the generated ML model to disk
    #     ---
    #     Parameter:
    #     1. generate ML model
    #     """
    #     model = model.export_model()
    #     model.summary()
    #     model.save("templates/output/model_autogluon", save_format="tf")
        return

    def classification(self):
        """
        Execute the classification task
        """
        self.__read_training_data()
        train_data = TabularDataset(self.__training_data_path)
        train_data[train_data.select_dtypes(['object']).columns] = train_data.select_dtypes(['object']) \
            .apply(lambda x: x.astype('category'))
        label = self.__configuration["configuration"]["target"]
        predictor = TabularPredictor(label=label, path="templates/output/model_autogluon").fit(train_data, time_limit=120)
        #clf.fit(self.__training_data_path, self.__json["configuration"]["target"], epochs=10)
        #self.__export_model(clf)
        return

    def regression(self):
        """
        Execute the regression task
        """
        #self.__read_training_data()
        #reg = ak.StructuredDataRegressor(overwrite=True, max_trials=3)
        #reg.fit(self.__training_data_path, self.__json["configuration"]["target"], epochs=10)
        #self.__export_model(reg)
        return