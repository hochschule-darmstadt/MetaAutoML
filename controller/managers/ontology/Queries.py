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

"""
SPARQL query to retrieve all configuration options with their corresponding values of a given automl and a given task
"""
ONTOLOGY_QUERY_GET_CONFIGURATION_BY_AUTOML_ID_AND_TASK_ID = """
        PREFIX : <http://h-da.de/ml-ontology/>

        SELECT ?param_iri ?param_label ?param_type ?broader_iri ?broader_label ?value_iri ?value_label
        WHERE {
                ?ci a :Configuration_item ;
                        :category :task_configuration ;
                        :automl_solution ?auto_ml_iri ;
                        :ml_task ?task_iri ;
                        :parameter_value ?param_iri .
                ?param_iri :parameter_value ?value_iri ;
                        skos:prefLabel ?param_label ;
						skos:broader ?broader_iri ;
                        :has_datatype ?param_type .
                ?value_iri skos:prefLabel ?value_label .
				?broader_iri skos:prefLabel ?broader_label .
        }
        """
