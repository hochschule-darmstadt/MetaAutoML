# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: AdapterService.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
)

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


class AdapterReturnCode(betterproto.Enum):
    ADAPTER_RETURN_CODE_UNKNOWN = 0
    ADAPTER_RETURN_CODE_SUCCESS = 1
    ADAPTER_RETURN_CODE_PENDING = 2
    ADAPTER_RETURN_CODE_STATUS_UPDATE = 3
    ADAPTER_RETURN_CODE_ERROR = 100


@dataclass(eq=False, repr=False)
class StartAutoMlRequest(betterproto.Message):
    training_id: str = betterproto.string_field(1)
    dataset_id: str = betterproto.string_field(2)
    user_id: str = betterproto.string_field(3)
    dataset_path: str = betterproto.string_field(4)
    configuration: "StartAutoMlConfiguration" = betterproto.message_field(5)
    dataset_configuration: str = betterproto.string_field(6)


@dataclass(eq=False, repr=False)
class StartAutoMlConfiguration(betterproto.Message):
    task: str = betterproto.string_field(1)
    target: str = betterproto.string_field(2)
    runtime_limit: int = betterproto.int32_field(4)
    metric: str = betterproto.string_field(5)


@dataclass(eq=False, repr=False)
class StartAutoMlResponse(betterproto.Message):
    session_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GetAutoMlStatusRequest(betterproto.Message):
    session_id: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GetAutoMlStatusResponse(betterproto.Message):
    return_code: "AdapterReturnCode" = betterproto.enum_field(1)
    status_update: str = betterproto.string_field(2)
    path: str = betterproto.string_field(3)
    test_score: float = betterproto.float_field(4)
    validation_score: float = betterproto.float_field(5)
    prediction_time: float = betterproto.float_field(6)
    library: str = betterproto.string_field(7)
    model: str = betterproto.string_field(8)


@dataclass(eq=False, repr=False)
class ExplainModelRequest(betterproto.Message):
    data: str = betterproto.string_field(1)
    process_json: str = betterproto.string_field(2)
    session_id: str = betterproto.string_field(3)


@dataclass(eq=False, repr=False)
class ExplainModelResponse(betterproto.Message):
    probabilities: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class PredictModelRequest(betterproto.Message):
    process_json: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class PredictModelResponse(betterproto.Message):
    predictions: List[str] = betterproto.string_field(1)
    predictiontime: float = betterproto.float_field(2)
    result_path: str = betterproto.string_field(3)


class AdapterServiceStub(betterproto.ServiceStub):
    async def start_auto_ml(
        self,
        start_auto_ml_request: "StartAutoMlRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "StartAutoMlResponse":
        return await self._unary_unary(
            "/AdapterService/StartAutoMl",
            start_auto_ml_request,
            StartAutoMlResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_auto_ml_status(
        self,
        get_auto_ml_status_request: "GetAutoMlStatusRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetAutoMlStatusResponse":
        return await self._unary_unary(
            "/AdapterService/GetAutoMlStatus",
            get_auto_ml_status_request,
            GetAutoMlStatusResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def explain_model(
        self,
        explain_model_request: "ExplainModelRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "ExplainModelResponse":
        return await self._unary_unary(
            "/AdapterService/ExplainModel",
            explain_model_request,
            ExplainModelResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def predict_model(
        self,
        predict_model_request: "PredictModelRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "PredictModelResponse":
        return await self._unary_unary(
            "/AdapterService/PredictModel",
            predict_model_request,
            PredictModelResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class AdapterServiceBase(ServiceBase):
    async def start_auto_ml(
        self, start_auto_ml_request: "StartAutoMlRequest"
    ) -> "StartAutoMlResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_auto_ml_status(
        self, get_auto_ml_status_request: "GetAutoMlStatusRequest"
    ) -> "GetAutoMlStatusResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def explain_model(
        self, explain_model_request: "ExplainModelRequest"
    ) -> "ExplainModelResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def predict_model(
        self, predict_model_request: "PredictModelRequest"
    ) -> "PredictModelResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_start_auto_ml(
        self, stream: "grpclib.server.Stream[StartAutoMlRequest, StartAutoMlResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.start_auto_ml(request)
        await stream.send_message(response)

    async def __rpc_get_auto_ml_status(
        self,
        stream: "grpclib.server.Stream[GetAutoMlStatusRequest, GetAutoMlStatusResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_auto_ml_status(request)
        await stream.send_message(response)

    async def __rpc_explain_model(
        self, stream: "grpclib.server.Stream[ExplainModelRequest, ExplainModelResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.explain_model(request)
        await stream.send_message(response)

    async def __rpc_predict_model(
        self, stream: "grpclib.server.Stream[PredictModelRequest, PredictModelResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.predict_model(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/AdapterService/StartAutoMl": grpclib.const.Handler(
                self.__rpc_start_auto_ml,
                grpclib.const.Cardinality.UNARY_UNARY,
                StartAutoMlRequest,
                StartAutoMlResponse,
            ),
            "/AdapterService/GetAutoMlStatus": grpclib.const.Handler(
                self.__rpc_get_auto_ml_status,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetAutoMlStatusRequest,
                GetAutoMlStatusResponse,
            ),
            "/AdapterService/ExplainModel": grpclib.const.Handler(
                self.__rpc_explain_model,
                grpclib.const.Cardinality.UNARY_UNARY,
                ExplainModelRequest,
                ExplainModelResponse,
            ),
            "/AdapterService/PredictModel": grpclib.const.Handler(
                self.__rpc_predict_model,
                grpclib.const.Cardinality.UNARY_UNARY,
                PredictModelRequest,
                PredictModelResponse,
            ),
        }