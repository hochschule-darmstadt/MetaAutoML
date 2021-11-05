import unittest
import Controller_pb2
from RdfManager import RdfManager

class TestRdfManager(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        self.__rdfManager = RdfManager()
        return super().__init__(methodName=methodName)

    ###GetCompatibleAutoMlSolutions unit test
    def test_GetCompatibleAutoMlSolutions_noTaskParameter(self):
        request = Controller_pb2.GetCompatibleAutoMlSolutionsRequest()
        request.configuration["somethingElse"] = "someConfigItem"
        result = self.__rdfManager.GetCompatibleAutoMlSolutions(request)
        self.assertEqual(result.AutoMlSolutions[0], "Task parameter missing")

    def test_GetCompatibleAutoMlSolutions_emptyTaskParameterValue(self):
        request = Controller_pb2.GetCompatibleAutoMlSolutionsRequest()
        request.configuration["task"] = ""
        result = self.__rdfManager.GetCompatibleAutoMlSolutions(request)
        self.assertEqual(result.AutoMlSolutions[0], "Task parameter value missing")

    def test_GetCompatibleAutoMlSolutions_Success(self):
        request = Controller_pb2.GetCompatibleAutoMlSolutionsRequest()
        request.configuration["task"] = "binary classification"
        result = self.__rdfManager.GetCompatibleAutoMlSolutions(request)
        self.assertTrue(len(result.AutoMlSolutions) > 0)
        
    ###GetDatasetCompatibleTasks unit test
    def test_GetDatasetCompatibleTasks_emptyDatasetNameParameterValue(self):
        request = Controller_pb2.GetDatasetCompatibleTasksRequest()
        request.datasetName = ""
        result = self.__rdfManager.GetDatasetCompatibleTasks(request)
        self.assertEqual(result.tasks[0], "Dataset name parameter empty")

    def test_GetDatasetCompatibleTasks_Success(self):
        request = Controller_pb2.GetDatasetCompatibleTasksRequest()
        request.datasetName = "Titanic.csv"
        result = self.__rdfManager.GetDatasetCompatibleTasks(request)
        self.assertTrue(len(result.tasks) > 0)

if __name__ =='__main__':
    unittest.main()