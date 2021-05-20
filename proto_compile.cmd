py -m grpc_tools.protoc -I ./service/protobufs --python_out=. --grpc_python_out=. --python_out=./service/snake-server --grpc_python_out=./service/snake-server ./service/protobufs/snake.proto
