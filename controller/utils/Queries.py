###Retrive all active and with task compatible AutoMLs
ONTOLOGY_QUERY_GET_ACTIVE_AUTOML_FOR_TASK = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?automl
            WHERE {
            ?automl a :AutoML_solution;
                      :supported_by_oma_ml "true" ;
                      :can_perform ?p .
            ?p skos:prefLabel ?task .
            }
            """
            
###Retrive all active and with library compatible AutoMLs
ONTOLOGY_QUERY_GET_ACTIVE_AUTOML_FOR_LIBRARY = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?automlTask
            WHERE {
            ?automlTask a :AutoML_solution;
                      :supported_by_oma_ml "true" ;
                      :can_perform ?l .
            ?l skos:prefLabel ?library .
            }
            """

###Retrieve all compatible tasks for a dataset type
ONTOLOGY_QUERY_GET_TASKS_FOR_DATASET_TYPE = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?task
            WHERE {
            ?t a :ML_task ;
                       :has_dataset_type ?set ;
                       skos:prefLabel ?task .
            ?set a :Enum ;
                       skos:prefLabel "tabular" .
            }
            """

###Retrieve all ML libraries compatible with a given task
ONTOLOGY_QUERY_GET_SUPPORTED_MACHINE_LEARNING_LIBRARY = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT DISTINCT ?library
            WHERE {
            ?automl a :AutoML_solution ;
                       :can_perform ?task ;
                       :supported_by_oma_ml "true" ;
                       :used_for ?lib .
            ?task a :ML_task ;
                       skos:prefLabel ?taskName .
            ?lib a :ML_library ;
                        skos:prefLabel ?library .
            }
            """
            
#Retreive all dataset types          
ONTOLOGY_QUERY_GET_DATASET_TYPES = """
            PREFIX : <http://h-da.de/ml-ontology/> 
            SELECT ?type
            WHERE {
                    ?type a :Enum ;
                            :category :dataset_type ;
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
