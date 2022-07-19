###Retrieve all active ML libraries compatible with a given task
ONTOLOGY_QUERY_GET_SUPPORTED_ML_LIBRARIES_FOR_TASK = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT DISTINCT ?lib
            WHERE {
            ?automl a :AutoML_solution ;
                       :can_perform ?task ;
                       :supported_by_oma_ml "True" ;
                       :used_for ?lib .
            }
            """

###Retrive all ML solutions compatible with a given task and libraries
ONTOLOGY_QUERY_GET_COMPATIBLE_AUTO_ML_SOLUTIONS_FOR_TASK_AND_LIBRARIES = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT DISTINCT ?automl
            WHERE {
            ?automl a :AutoML_solution ;
                       :can_perform ?task ;
                       :supported_by_oma_ml "True" ;
                       :used_for ?lib .
            }
            """
###Retrive all ML solutions compatible with a given task
ONTOLOGY_QUERY_GET_COMPATIBLE_AUTO_ML_SOLUTIONS_FOR_TASK = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT DISTINCT ?automl
            WHERE {
            ?automl a :AutoML_solution ;
                       :can_perform ?task ;
                       :supported_by_oma_ml "True" .
            }
            """

###Retrieve all compatible tasks for a dataset type
ONTOLOGY_QUERY_GET_TASKS_FOR_DATASET_TYPE = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?task
            WHERE {
            ?task a :ML_task ;
                       :has_dataset_type ?dataset_type .
            }
            """
            
#Retreive all dataset types          
ONTOLOGY_QUERY_GET_DATASET_TYPES = """
            PREFIX : <http://h-da.de/ml-ontology/> 
            SELECT ?type
            WHERE {
                    ?type a :Enum ;
                            :category ?dataset_type ;
                            :supported_by_oma_ml "true" .
            } 
            """

#Retrieve all object information by id
ONTOLOGY_QUERY_GET_ALL_DETAILS_BY_ID = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?p ?o
            WHERE {
            ?s ?p ?o
            }
            """