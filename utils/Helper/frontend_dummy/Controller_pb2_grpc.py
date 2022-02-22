# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import Controller_pb2 as Controller__pb2


class ControllerServiceStub(object):
    """includes all gRPC functions available for the client frontend
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetAutoMlModel = channel.unary_unary(
                '/ControllerService/GetAutoMlModel',
                request_serializer=Controller__pb2.GetAutoMlModelRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetAutoMlModelResponse.FromString,
                )
        self.GetCompatibleAutoMlSolutions = channel.unary_unary(
                '/ControllerService/GetCompatibleAutoMlSolutions',
                request_serializer=Controller__pb2.GetCompatibleAutoMlSolutionsRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetCompatibleAutoMlSolutionsResponse.FromString,
                )
        self.GetDatasets = channel.unary_unary(
                '/ControllerService/GetDatasets',
                request_serializer=Controller__pb2.GetDatasetsRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetDatasetsResponse.FromString,
                )
        self.GetDataset = channel.unary_unary(
                '/ControllerService/GetDataset',
                request_serializer=Controller__pb2.GetDatasetRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetDatasetResponse.FromString,
                )
        self.GetSessions = channel.unary_unary(
                '/ControllerService/GetSessions',
                request_serializer=Controller__pb2.GetSessionsRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetSessionsResponse.FromString,
                )
        self.GetSessionStatus = channel.unary_unary(
                '/ControllerService/GetSessionStatus',
                request_serializer=Controller__pb2.GetSessionStatusRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetSessionStatusResponse.FromString,
                )
        self.GetSupportedMlLibraries = channel.unary_unary(
                '/ControllerService/GetSupportedMlLibraries',
                request_serializer=Controller__pb2.GetSupportedMlLibrariesRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetSupportedMlLibrariesResponse.FromString,
                )
        self.GetTabularDatasetColumnNames = channel.unary_unary(
                '/ControllerService/GetTabularDatasetColumnNames',
                request_serializer=Controller__pb2.GetTabularDatasetColumnNamesRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetTabularDatasetColumnNamesResponse.FromString,
                )
        self.GetDatasetCompatibleTasks = channel.unary_unary(
                '/ControllerService/GetDatasetCompatibleTasks',
                request_serializer=Controller__pb2.GetDatasetCompatibleTasksRequest.SerializeToString,
                response_deserializer=Controller__pb2.GetDatasetCompatibleTasksResponse.FromString,
                )
        self.UploadDatasetFile = channel.unary_unary(
                '/ControllerService/UploadDatasetFile',
                request_serializer=Controller__pb2.UploadDatasetFileRequest.SerializeToString,
                response_deserializer=Controller__pb2.UploadDatasetFileResponse.FromString,
                )
        self.StartAutoMLprocess = channel.unary_unary(
                '/ControllerService/StartAutoMLprocess',
                request_serializer=Controller__pb2.StartAutoMLprocessRequest.SerializeToString,
                response_deserializer=Controller__pb2.StartAutoMLprocessResponse.FromString,
                )
        self.TestAutoML = channel.unary_unary(
                '/ControllerService/TestAutoML',
                request_serializer=Controller__pb2.TestAutoMLRequest.SerializeToString,
                response_deserializer=Controller__pb2.TestAutoMLResponse.FromString,
                )


class ControllerServiceServicer(object):
    """includes all gRPC functions available for the client frontend
    """

    def GetAutoMlModel(self, request, context):
        """return the generated model as a .zip for one AutoML by its session id
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCompatibleAutoMlSolutions(self, request, context):
        """return a list of AutoML solutions compatible with the current configuration
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetDatasets(self, request, context):
        """return all datasets of a specific type
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetDataset(self, request, context):
        """
        returns details of a specified dataset.

        The result is a list of TableColumns containing:
        name: the name of the dataset
        datatype: the datatype of the column
        firstEntries: the first couple of rows of the dataset
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSessions(self, request, context):
        """return a list of all sessions the controller has knowledge of
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSessionStatus(self, request, context):
        """return the status of a specific session. The result is a session status and a list of the automl output and its status
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetSupportedMlLibraries(self, request, context):
        """return all supported machine learning libraries for a specific task (by searching supported AutoML)
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetTabularDatasetColumnNames(self, request, context):
        """return all the column names of a tabular dataset
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetDatasetCompatibleTasks(self, request, context):
        """return all supported AutoML tasks
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UploadDatasetFile(self, request, context):
        """upload a new dataset file as bytes to the controller repository
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def StartAutoMLprocess(self, request, context):
        """start a new AutoML run, using the provided configuration
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TestAutoML(self, request, context):
        """test an existing AutoML
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ControllerServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetAutoMlModel': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAutoMlModel,
                    request_deserializer=Controller__pb2.GetAutoMlModelRequest.FromString,
                    response_serializer=Controller__pb2.GetAutoMlModelResponse.SerializeToString,
            ),
            'GetCompatibleAutoMlSolutions': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCompatibleAutoMlSolutions,
                    request_deserializer=Controller__pb2.GetCompatibleAutoMlSolutionsRequest.FromString,
                    response_serializer=Controller__pb2.GetCompatibleAutoMlSolutionsResponse.SerializeToString,
            ),
            'GetDatasets': grpc.unary_unary_rpc_method_handler(
                    servicer.GetDatasets,
                    request_deserializer=Controller__pb2.GetDatasetsRequest.FromString,
                    response_serializer=Controller__pb2.GetDatasetsResponse.SerializeToString,
            ),
            'GetDataset': grpc.unary_unary_rpc_method_handler(
                    servicer.GetDataset,
                    request_deserializer=Controller__pb2.GetDatasetRequest.FromString,
                    response_serializer=Controller__pb2.GetDatasetResponse.SerializeToString,
            ),
            'GetSessions': grpc.unary_unary_rpc_method_handler(
                    servicer.GetSessions,
                    request_deserializer=Controller__pb2.GetSessionsRequest.FromString,
                    response_serializer=Controller__pb2.GetSessionsResponse.SerializeToString,
            ),
            'GetSessionStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.GetSessionStatus,
                    request_deserializer=Controller__pb2.GetSessionStatusRequest.FromString,
                    response_serializer=Controller__pb2.GetSessionStatusResponse.SerializeToString,
            ),
            'GetSupportedMlLibraries': grpc.unary_unary_rpc_method_handler(
                    servicer.GetSupportedMlLibraries,
                    request_deserializer=Controller__pb2.GetSupportedMlLibrariesRequest.FromString,
                    response_serializer=Controller__pb2.GetSupportedMlLibrariesResponse.SerializeToString,
            ),
            'GetTabularDatasetColumnNames': grpc.unary_unary_rpc_method_handler(
                    servicer.GetTabularDatasetColumnNames,
                    request_deserializer=Controller__pb2.GetTabularDatasetColumnNamesRequest.FromString,
                    response_serializer=Controller__pb2.GetTabularDatasetColumnNamesResponse.SerializeToString,
            ),
            'GetDatasetCompatibleTasks': grpc.unary_unary_rpc_method_handler(
                    servicer.GetDatasetCompatibleTasks,
                    request_deserializer=Controller__pb2.GetDatasetCompatibleTasksRequest.FromString,
                    response_serializer=Controller__pb2.GetDatasetCompatibleTasksResponse.SerializeToString,
            ),
            'UploadDatasetFile': grpc.unary_unary_rpc_method_handler(
                    servicer.UploadDatasetFile,
                    request_deserializer=Controller__pb2.UploadDatasetFileRequest.FromString,
                    response_serializer=Controller__pb2.UploadDatasetFileResponse.SerializeToString,
            ),
            'StartAutoMLprocess': grpc.unary_unary_rpc_method_handler(
                    servicer.StartAutoMLprocess,
                    request_deserializer=Controller__pb2.StartAutoMLprocessRequest.FromString,
                    response_serializer=Controller__pb2.StartAutoMLprocessResponse.SerializeToString,
            ),
            'TestAutoML': grpc.unary_unary_rpc_method_handler(
                    servicer.TestAutoML,
                    request_deserializer=Controller__pb2.TestAutoMLRequest.FromString,
                    response_serializer=Controller__pb2.TestAutoMLResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ControllerService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ControllerService(object):
    """includes all gRPC functions available for the client frontend
    """

    @staticmethod
    def GetAutoMlModel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetAutoMlModel',
            Controller__pb2.GetAutoMlModelRequest.SerializeToString,
            Controller__pb2.GetAutoMlModelResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetCompatibleAutoMlSolutions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetCompatibleAutoMlSolutions',
            Controller__pb2.GetCompatibleAutoMlSolutionsRequest.SerializeToString,
            Controller__pb2.GetCompatibleAutoMlSolutionsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetDatasets(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetDatasets',
            Controller__pb2.GetDatasetsRequest.SerializeToString,
            Controller__pb2.GetDatasetsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetDataset(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetDataset',
            Controller__pb2.GetDatasetRequest.SerializeToString,
            Controller__pb2.GetDatasetResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetSessions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetSessions',
            Controller__pb2.GetSessionsRequest.SerializeToString,
            Controller__pb2.GetSessionsResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetSessionStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetSessionStatus',
            Controller__pb2.GetSessionStatusRequest.SerializeToString,
            Controller__pb2.GetSessionStatusResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetSupportedMlLibraries(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetSupportedMlLibraries',
            Controller__pb2.GetSupportedMlLibrariesRequest.SerializeToString,
            Controller__pb2.GetSupportedMlLibrariesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetTabularDatasetColumnNames(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetTabularDatasetColumnNames',
            Controller__pb2.GetTabularDatasetColumnNamesRequest.SerializeToString,
            Controller__pb2.GetTabularDatasetColumnNamesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetDatasetCompatibleTasks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/GetDatasetCompatibleTasks',
            Controller__pb2.GetDatasetCompatibleTasksRequest.SerializeToString,
            Controller__pb2.GetDatasetCompatibleTasksResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UploadDatasetFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/UploadDatasetFile',
            Controller__pb2.UploadDatasetFileRequest.SerializeToString,
            Controller__pb2.UploadDatasetFileResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def StartAutoMLprocess(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/StartAutoMLprocess',
            Controller__pb2.StartAutoMLprocessRequest.SerializeToString,
            Controller__pb2.StartAutoMLprocessResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TestAutoML(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ControllerService/TestAutoML',
            Controller__pb2.TestAutoMLRequest.SerializeToString,
            Controller__pb2.TestAutoMLResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)