from .AbstractAgent import IAbstractBlackboardAgent

class DataAnalysisAgent(IAbstractBlackboardAgent):
    def CanContribute(self) -> bool:
        return (
            self.blackboard.common_state.get('phase') == 'data_preparation' and
            self.blackboard.common_state.get('dataset_metrics') == None
        )
    
    def DoContribute(self) -> None:
        # TODO: Load real input dataset metrics (from file/db?)

        dataset_metrics = {
            'number_of_columns': 50,
            'number_of_rows': 1234567,
            'na_columns': [],
            'high_na_rows': [],
            'outlier': {}
        }

        self.blackboard.common_state.update({
            'dataset_metrics': dataset_metrics
        })

        return dataset_metrics