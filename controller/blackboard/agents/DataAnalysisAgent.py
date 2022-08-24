from .AbstractAgent import IAbstractBlackboardAgent
from persistence.data_storage import DataStorage

class DataAnalysisAgent(IAbstractBlackboardAgent):
    blackboard_key = 'dataset_analysis'

    def __init__(self, blackboard, controller, dataset_id: str, data_storage: DataStorage):
        super().__init__(blackboard, controller, 'data-analysis')
        self.dataset_id = dataset_id
        self.data_storage = data_storage

    def CanContribute(self) -> bool:
        return (
            self.blackboard.GetState('dataset_analysis') is None and
            self.blackboard.GetState('session') is not None
        )
    
    def DoContribute(self) -> None:
        session_username = self.blackboard.GetState('session', {}).get('configuration', {}).get('username')
        found, dataset = self.data_storage.GetDataset(session_username, self.dataset_id)

        dataset_analysis = dataset.get('analysis', {}).get('basic_analysis') if found else {}
        dataset_analysis = {key: dataset_analysis[key] for key in dataset_analysis if key not in ['outlier']} # FIXME: Remove (for testing purposes)
        self.UpdateState(dataset_analysis)

        # The dataset analysis has to be loaded only once, therefore unregister the agent again
        self.Unregister()

        return dataset_analysis