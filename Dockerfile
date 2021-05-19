FROM python

COPY server.py .
COPY snake.proto .
COPY snake_pb2.py .
COPY snake_pb2_grpc.py .
COPY cert.pem .
COPY key.pem .

RUN python -m pip install --upgrade pip
RUN python -m pip install grpcio
RUN python -m pip install grpcio-tools

EXPOSE 50051
ENTRYPOINT ["python", "server.py"]