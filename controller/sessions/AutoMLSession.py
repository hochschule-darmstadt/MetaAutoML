import atexit, json
from Controller_bgrpc import *
from IAutoMLManager import IAutoMLManager
from persistence.data_storage import DataStorage

class AutoMLSession(object):
    """
    Implementation of an AutoML session object
    """

    def __init__(self, session_id: int, dataset_id: str, configuration: StartAutoMlProcessRequest, data_storage: DataStorage, username: str):
        """
        Init a new instance of AutoMLSession
        ---
        Parameter
        1. id: session id as an int
        2. configuration: session configuration
        """
        self.__id = session_id
        self.configuration = configuration
        self.automls = []
        self.data_storage = data_storage
        self.username = username

        from blackboard.Blackboard import Blackboard
        from blackboard.Controller import StrategyController
        self.blackboard = Blackboard()
        self.controller = StrategyController(self.blackboard, self)

        from blackboard.agents.AutoMLSessionAgent import AutoMLSessionAgent
        session_agent = AutoMLSessionAgent(blackboard=self.blackboard, controller=self.controller, session=self)
        from blackboard.agents.DataAnalysisAgent import DataAnalysisAgent
        data_analysis_agent = DataAnalysisAgent(blackboard=self.blackboard, controller=self.controller, dataset_id=dataset_id)

        self.controller.OnEvent('phase_updated', self.handle_phase_update)
        self.controller.SetPhase('preprocessing')
        self.controller.StartTimer()
        # IDEA: atexit.register(self.controller.StopTimer)

    def add_automl_to_training(self, automl: IAutoMLManager):
        """
        Add an AutoML to the current session
        ---
        Parameter
        1. automl the automl object implementing the IAutoMLManager
        """
        self.automls.append(automl)
        
        from blackboard.agents.AutoMLRunAgent import AutoMLRunAgent
        automl_run_agent = AutoMLRunAgent(blackboard=self.blackboard, controller=self.controller, manager=automl)

    def handle_phase_update(self, meta, controller):
        """
        Handles phase updates throughout the session (caused by the strategy controller)
        ---
        Parameter
        1. The event meta (contains a dict holding the "old_phase" and "new_phase")
        1. The strategy controller instance that caused the event
        """
        if meta.get('old_phase') == 'preprocessing' and meta.get('new_phase') == 'running':
            # Preprocessing finished, start the AutoML training
            self.start_automl_training()

    def start_automl_training(self):
        """
        Starts all AutoMLs added to the current session
        """
        for automl in self.automls:
            automl.start()

    def get_id(self) -> str:
        """
        Get the session id
        ---
        Return session id as str
        """
        return str(self.__id)

    def get_configuration(self) -> str:
        """
        Get the session configuration
        ---
        Return session configuration as dict
        """
        return self.configuration.to_dict()

    def get_automl_model(self, request: GetAutoMlModelRequest) -> GetAutoMlModelResponse:
        """
        Get the AutoML model of requested AutoML
        ---
        Parameter
        1. request: info about what AutoML the model is to be retrieved
        ---
        Return AutoML model as Controller_pb2.GetAutoMlModelResponse
        """
        for automl in self.automls:
            if automl.name == request.auto_ml:
                return automl.get_automl_model()

    def get_session_status(self) -> GetTrainingResponse:
        """
        Get the session status
        ---
        Return the session status as Controller_pb2.GetSessionStatusResponse
        """

        response = GetTrainingResponse(configuration=self.configuration.configuration,
                                                            dataset_configuration=self.configuration.dataset_configuration,
                                                           required_auto_mls=[automl.name for automl in self.automls],
                                                           runtime_constraints=self.configuration.runtime_constraints)
        response.status = SessionStatus.SESSION_STATUS_COMPLETED
        response.dataset = self.configuration.dataset
        response.task = self.configuration.task

        for automl in self.automls:
            response.automls.append(automl.get_status())
            if automl.is_running():
                response.status = SessionStatus.SESSION_STATUS_BUSY

        return response
