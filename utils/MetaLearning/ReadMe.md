How to update the parameters for the runtime prediction:

1. Get the newest Version of the training data (pay attention in the export to extract the models by their task)
2. Add the data ( trainings, models, datasets) to the MongoDBCompass by adding a new collection and adding subcollections of that. Add each of the exported JSON files to the subcollection. All model.json files should be together in the model's collection no matter the task
To avoid changing variable names name the collection “new_trainings” and the names for the subcollections are “trainings”, “datasets” and “models” like in the picture
3. For updating the parameters run the script update_runtume_parametes in the MetaLearning folder. You only have to change the database connection or collection names in case you gave them other names or you used another URI.
4. After running the script the updated runtime prediction parameters are in the correct folder for the new predictions
