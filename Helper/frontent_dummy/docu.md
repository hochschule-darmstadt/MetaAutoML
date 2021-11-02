# 1) Start MetaAutoML-Controller
- PYTHONPATH needs to be specified "/interfaces:/managers:/managers/structureddata:/sessions"
- python Controller.py
- --> server start 
- --> `Controller.py` --> wait for client line 112f

# 2) Start MetaAutoML-Adapter-AutoKeras
- Precondition: Download titanic_train_1.csv from here: https://www.kaggle.com/c/titanic/data?select=train.csv --> Store it in MetaAutoML-Controller/omaml/datasets
- PYTHONPATH needs to be specified "/AutoMLs:/templates:/templates/output"
- `python Adapter_AutoKeras.py`

# 3) Start Dummy and request session status
- `python dummy.py start-automl`
- `python dummy.py get-session-status 1`



# Calls in MetaAutoML-Controller 
- gRPC call from Client (Dummy) to Controller
- --> incoming call to specific function
- e.g. startAutoMLprocess
```
--> startAutoMLprocess
     --> call in ControllerManager.py
        --> startAutoML 
            --> StructuredDataManager.py
                --> startAutoML
                    --> AutoKerasManager.py
                        --> Thread.start calls run() 
                            --> connect as Client to AutoKeras (Server)
                           
``` 

# Calls in Adapter-AutoKeras
- gRPC call from Client (MetaAutoML-Controller) to Adapter-AutoKeras
- --> incoming call to StartAutoML
```
--> calls AutoML.py as subprocess
    --> runs classification task in StructuredDataAutoML
--> generate report
--> returns result to controller
```
- hints: currently Adapter_AutoKeras has multiple hardcoded paths: e.g. zip_content_path = os.path.join(BASE_DIR, "Adapter-AutoKeras/templates/output") --> project dir needs to be "Adapter-AutoKeras"
