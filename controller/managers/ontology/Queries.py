"""
SPARQL query to retrieve all supported ML library IRIs for a given task
"""
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

"""
SPARQL query to retrieve all AutoML solution IRIs by task and ML library
"""
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
"""
SPARQL query to retrieve AutoML solution IRIs by task
"""
ONTOLOGY_QUERY_GET_COMPATIBLE_AUTO_ML_SOLUTIONS_FOR_TASK = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT DISTINCT ?automl
            WHERE {
            ?automl a :AutoML_solution ;
                       :can_perform ?task ;
                       :supported_by_oma_ml "True" .
            }
            """

"""
SPARQL query to retrieve task IRIs by dataset type
"""
ONTOLOGY_QUERY_GET_TASKS_FOR_DATASET_TYPE = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?task
            WHERE {
            ?task a :ML_task ;
                        :has_dataset_type ?dataset_type ;
                        :supported_by_oma_ml "True" .
            }
            """
            
"""
SPARQL query to retrieve all dataset type IRIs
"""     
ONTOLOGY_QUERY_GET_DATASET_TYPES = """
            PREFIX : <http://h-da.de/ml-ontology/> 
            SELECT ?type
            WHERE {
                    ?type a :Enum ;
                            :category ?dataset_type ;
                            :supported_by_oma_ml "True" .
            } 
            """

"""
SPARQL query to retrieve all object informations by IRI

        Response example:
        :tabular_classification a :ML_task ;
            skos:prefLabel "tabular classification" ;
            skos:broader :classification ;
            :belongs_to :supervised_learning ;
            :has_dataset_type :tabular .

"""
ONTOLOGY_QUERY_GET_ALL_DETAILS_BY_ID = """
            PREFIX : <http://h-da.de/ml-ontology/>
            SELECT ?p ?o
            WHERE {
            ?s ?p ?o
            }
            """