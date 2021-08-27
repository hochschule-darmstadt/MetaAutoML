import zope.interface
import Controller_pb2
import Controller_pb2_grpc

class IAutoMLManager(zope.interface.Interface):
    """
    Interface representing the functionality any AutoML manager must provide
    """
    
    def GetAutoMlModel(self) -> Controller_pb2.GetSessionStatusResponse:
        """
        Get the generated AutoML model
        ---
        Return the AutoML model if the run is concluded
        """
        pass

    def GetStatus(self) -> Controller_pb2.AutoMLStatus:
        """
        Get the execution status of the AutoML
        ---
        Return the current AutoML status
        """
        pass

    def IsRunning(self) -> bool:
        """
        Check if the AutoML is currently running
        ---
        Return bool if AutoML is running => true
        """
        pass
