
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
            ?dataset a :ML_dataset ;
                       skos:prefLabel "tabular data" ;
                       :used_for ?t .
            ?t a :ML_task ;
                       skos:prefLabel ?task .

            }
            """