import pymongo
import helping_scripts.ReadDatabase as readDatabase
import helping_scripts.CaluclateRuntimeConvergenz as CaluclateRuntimeConvergenz
import helping_scripts.TrainModels as train_models
import os

"""
This script is for updating the runtime prediction parameters

For calculating the new runtime prediction parameters edit the following variables or rename the collections in MongoDBCompass
"""
# Set here your database connection
client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")

# fill in the name of your database
db = client["ai-optimization"]

# Collection Name
#ändere die Namen demenstrpchend nach den collection namen aus deiner Datenbank ab
trainings = db["trainings"]
datasets = db["datasets"]
models = db["models"]

# Only edit when changing the folder structure
file_path = "../data"


#Variables for the regared measures
measure_classification = ":balanced_accuracy"
measure_regression = ":rooted_mean_squared_error"

#reads the information from the database and saves them in a csv file
readDatabase.readDatabase(trainings, datasets, models, file_path, measure_classification, measure_regression)

#calculate the best runtime limit per dataset
CaluclateRuntimeConvergenz.caluclate_runtime_convergenz(file_path, measure_classification, measure_regression)

#update runtime prediction parameters
train_models.calculate_new_parameters(file_path)

