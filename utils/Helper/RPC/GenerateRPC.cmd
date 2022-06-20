python3 -m grpc_tools.protoc --proto_path=. --python_out=./controller --grpc_python_out=./controller Controller.proto
python3 -m grpc_tools.protoc --proto_path=. --python_out=./adapter --grpc_python_out=./adapter Adapter.proto

python -m grpc_tools.protoc -I . --python_betterproto_out=controller Controller.proto