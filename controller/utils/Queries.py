
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
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
            SELECT ?t 
            WHERE {
                    ?t a :Enum;
                :category :dataset_type .
            } 
            """