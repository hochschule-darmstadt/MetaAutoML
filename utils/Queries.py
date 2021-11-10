
###Retrive all active and with task compatible AutoMLs
ONTOLOGY_QUERY_GET_ACTIVE_AUTOML_FOR_TASK = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?automl
            WHERE {
            ?automl a :AutoML_solution;
                      :is_active "yes" ;
                      :can_perform ?p .
            ?p skos:prefLabel ?task .

            }
            """

ONTOLOGY_QUERY_GET_TASK_FOR_DATASET = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?task
            WHERE {
            ?set a :ML_dataset ;
                       skos:prefLabel ?dataset;
                       :used_for ?t .
            ?t a :ML_task ;
                       skos:prefLabel ?task .

            }
            """

ONTOLOGY_QUERY_GET_SUPPORTED_MACHINE_LEARNING_LIBRARY = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT DISTINCT ?library
            WHERE {
            ?automl a :AutoML_solution ;
                       :can_perform ?task ;
                       :is_active "yes" ;
                       :used_for ?lib .
            ?task a :ML_task ;
                       skos:prefLabel ?taskName .
            ?lib a :ML_library ;
                        skos:prefLabel ?library .
            }
            """