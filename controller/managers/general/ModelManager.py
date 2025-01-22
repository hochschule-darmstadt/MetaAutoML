import threading
from urllib import request
from DataStorage import DataStorage
from ControllerBGRPC import *
import json, logging, os
from AdapterRuntimeScheduler import AdapterRuntimeScheduler

class ModelManager:
    """The ModelManager provides all functionality related to Models objects
    """

    def __init__(self, data_storage: DataStorage, adapter_runtime_scheduler: AdapterRuntimeScheduler) -> None:
        """Initialize a new ModelManager instance

        Args:
            data_storage (DataStorage): The datastore instance to access MongoDB
        """
        self.__data_storage: DataStorage = data_storage
        self.__log = logging.getLogger('ModelManager')
        self.__log.setLevel(logging.getLevelName(os.getenv("SERVER_LOGGING_LEVEL")))
        self.__adapter_runtime_scheduler = adapter_runtime_scheduler


    def __model_object_to_rpc_object(self, user_id: str, model: dict) -> Model:
        """Convert a model record dictionary into the GRPC Model object

        Args:
            user_id (str): Unique user id saved within the MS Sql database of the frontend
            model (dict): The retrieved model record dictionary

        Raises:
            grpclib.GRPCError: grpclib.Status.UNAVAILABLE, raised when a dictionary field could not be read

        Returns:
            Model: The GRPC model object generated from the dictonary
        """
        try:
            self.__log.debug("__model_object_to_rpc_object: get all predictions for model")
            model_predictions = self.__data_storage.get_predictions(user_id, str(model["_id"]))
            self.__log.debug(f"__model_object_to_rpc_object: found {model_predictions.count} predictions")

            model_info = Model()
            model_info.id = str(model["_id"])
            model_info.training_id = model["training_id"]

            for prediction in model_predictions:
                prediction_detail = Prediction()
                prediction_detail.id = str(prediction["_id"])
                prediction_detail.model_id = prediction["model_id"]
                prediction_detail.live_dataset_path = prediction["live_dataset_path"]
                prediction_detail.prediction_path = prediction["prediction_path"]
                prediction_detail.status = prediction["status"]
                prediction_runtime_profile = PredictionRuntimeProfile()
                prediction_runtime_profile.start_time = prediction["runtime_profile"]["start_time"]
                prediction_runtime_profile.end_time = prediction["runtime_profile"]["end_time"]
                prediction_detail.runtime_profile = prediction_runtime_profile
                model_info.predictions.append(prediction_detail)

            model_info.status = model["status"]
            model_info.auto_ml_solution = model["auto_ml_solution"]
            model_info.ml_model_type = model["ml_model_type"]
            model_info.ml_library =  model["ml_library"]
            model_info.path = model["path"]
            model_info.test_score = json.dumps(model["test_score"])
            model_info.prediction_time =  model["prediction_time"]

            model_runtime_profile = ModelruntimeProfile()
            model_runtime_profile.start_time = model["runtime_profile"]["start_time"]
            model_runtime_profile.end_time = model["runtime_profile"]["end_time"]
            model_info.runtime_profile = model_runtime_profile

            model_info.status_messages[:] =  model["status_messages"]

            if not model.get("dashboard_path"):  # Returns None if key is missing
                model_info.dashboard_status = "inactive"
            else:
                model_info.dashboard_status = "active"
            #model_info.explanation = json.dumps(model["explanation"])

            if not "carbon_footprint" in model:
                        model["carbon_footprint"] = {"emissions": 0}
            model_info.emission = model["carbon_footprint"].get("emissions", 0)
            return model_info
        except Exception as e:
            self.__log.error(f"__model_object_to_rpc_object: Error while reading parameter for model {model.model_id}")
            self.__log.error(f"__model_object_to_rpc_object: exception: {e}")
            raise grpclib.GRPCError(grpclib.Status.UNAVAILABLE, f"Error while retrieving Model {model.model_id}")


    def get_models(
        self, get_models_request: "GetModelsRequest"
    ) -> "GetModelsResponse":
        """Get all datasets or get all datasets using an optional filter

        Args:
            get_models_request (GetModelsRequest): The GRPC request holding the user id and filters

        Returns:
            GetModelsResponse: The GRPC response holding the list of found models
        """
        response = GetModelsResponse()

        extended_pipeline = [
            # Stage 1: Add a field firstTestScore to the document, which is the first test score of the model
            {
                '$addFields': {
                    'firstTestScore': {
                        '$ifNull': [
                            {
                                '$first': {
                                    '$map': {
                                        'input': {
                                            '$objectToArray': '$test_score'
                                        },
                                        'as': 'score',
                                        'in': '$$score.v'
                                    }
                                }
                            }, 0
                        ]
                    }
                }
            },
            # Stage 2: Sort the models by the first test score
            {
                '$sort': {
                    'firstTestScore': -1
                }
            },
            # Stage 3: Lookup the predictions for each model
            {
                '$lookup': {
                    'from': 'predictions',
                    'let': {
                        'model_id': '$_id'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$eq': [
                                        {
                                            '$toObjectId': '$model_id'
                                        }, '$$model_id'
                                    ]
                                }
                            }
                        },
                        {
                            '$project': {
                                '_id': 0,
                                'id': {
                                    '$toString': '$_id'
                                },
                                'model_id': 1,
                                'live_dataset_path': 1,
                                'prediction_path': 1,
                                'status': 1,
                                'runtime_profile': 1
                            }
                        }
                    ],
                    'as': 'predictions'
                }
            },
            # Stage 4: Project the fields we want to return to match the gRPC Model object
            {
                '$project': {
                    # Convert the _id to a string
                    '_id': 0,
                    'id': {
                        '$toString': '$_id'
                    },
                    'training_id': 1,
                    'predictions': 1,
                    'status': 1,
                    'auto_ml_solution': 1,
                    'ml_model_type': 1,
                    'ml_library': 1,
                    'path': 1,
                    'test_score': 1,
                    'prediction_time': 1,
                    'runtime_profile': 1,
                    'status_messages': 1,
                    'explanation': 1,

                    # Check if the dashboard_path exists, if not set the dashboard_status to inactive else active
                    'dashboard_status': {
                        '$cond': [
                            {
                                '$ne': [
                                    {
                                        '$type': '$dashboard_path'
                                    }, 'missing'
                                ]
                            }, 'active', 'inactive'
                        ]
                    },
                    # Get the emissions from the carbon_footprint object, if it does not exist, set it to 0
                    'emission': {
                        '$ifNull': [
                            {
                                '$getField': {
                                    'field': 'emissions',
                                    'input': '$carbon_footprint'
                                }
                            },
                            0
                        ]
                    }
                }
            }
        ]

        self.__log.debug(f"get_models: get all models for dataset {get_models_request.dataset_id} for user {get_models_request.user_id}")
        all_models: list[dict[str, object]] = self.__data_storage.get_models(get_models_request.user_id, dataset_id=get_models_request.dataset_id, extended_pipeline=extended_pipeline)
        self.__log.debug(f"get_models: found {all_models.count} models for dataset {get_models_request.dataset_id} for user {get_models_request.user_id}")

        response.models = [
            Model(
                **{key: value for key, value in model.items() if key not in ['test_score', 'explanation', 'predictions', 'runtime_profile']},
                test_score=json.dumps(model.get("test_score", {})),
                explanation=json.dumps(model.get("explanation", {})),
                predictions=[
                    Prediction(
                        **{key: value for key, value in prediction.items() if key != 'runtime_profile'},
                        runtime_profile=PredictionRuntimeProfile(**prediction["runtime_profile"])
                    ) for prediction in model["predictions"]
                ],
                runtime_profile=ModelruntimeProfile(**model["runtime_profile"])
            ) for model in all_models
        ]

        return response

    def get_model(
        self, get_model_request: "GetModelRequest"
    ) -> "GetModelResponse":
        """Get model details for a specific model

        Args:
            get_model_request (GetModelRequest): The GRPC request holding the user id and and model id

        Raises:
            grpclib.GRPCError: grpclib.Status.NOT_FOUND, raised if no model record was found

        Returns:
            GetModelResponse: The GRPC response holding the found model
        """
        response = GetModelResponse()
        found, model = self.__data_storage.get_model(get_model_request.user_id, get_model_request.model_id)
        if not found:
            self.__log.error(f"get_training: model {get_model_request.model_id} for user {get_model_request.user_id} not found")
            raise grpclib.GRPCError(grpclib.Status.NOT_FOUND, f"Model {get_model_request.model_id} for user {get_model_request.user_id} not found, already deleted?")

        response.model = self.__model_object_to_rpc_object(get_model_request.user_id, model)
        return response


    def delete_model(
        self, delete_model_request: "DeleteModelRequest"
    ) -> "DeleteModelResponse":
        """Delete a model from database and disc

        Args:
            delete_model_request (DeleteModelRequest): The GRPC request containing the user id, model id

        Returns:
            DeleteModelResponse: The empty GRPC response
        """
        self.__log.debug(f"delete_model: deleting model {delete_model_request.model_id}, of user {delete_model_request.user_id}")
        amount_delelted_models = self.__data_storage.delete_model(delete_model_request.user_id, delete_model_request.model_id)
        self.__log.debug(f"delete_model: model deleted {amount_delelted_models}")
        return DeleteModelResponse()

    def start_explainer_dashboard(
        self, start_dashboard_request: "StartDashboardRequest"
    ) -> "StartDashboardResponse":
        """Start an ExplainerDashboard from disc

        Args:
            start_dashboard_request (StartDashboardRequest): The GRPC request containing the model id

        Returns:
            start_dashboard_response: The empty GRPC response
        """
        self.__log.debug(f"start_explainer_dashboard: start dashboard of model {start_dashboard_request.model_id}")
        return self.__adapter_runtime_scheduler.start_new_explainer_dashboard(start_dashboard_request.user_id, start_dashboard_request.model_id)

    def stop_explainer_dashboard(
        self, stop_dashboard_request: "StopDashboardRequest"
    ) -> "StopDashboardResponse":
        """Stop an ExplainerDashboard

        Args:
            stop_dashboard_request (StioDashboardRequest): The GRPC request containing the model id

        Returns:
            stop_dashboard_response: The empty GRPC response
        """
        self.__log.debug(f"stop_explainer_dashboard: stop dashboard of session {stop_dashboard_request.session_id}")

        return self.__adapter_runtime_scheduler.stop_explainer_dashboard(stop_dashboard_request.session_id)
