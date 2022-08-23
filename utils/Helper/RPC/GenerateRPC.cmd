python -m grpc_tools.protoc --proto_path=./adapter --python_out=./adapter --grpc_python_out=./adapter Adapter.proto

python -m grpc_tools.protoc -I . --python_betterproto_out=out ControllerService.proto