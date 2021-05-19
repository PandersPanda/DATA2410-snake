FROM python

RUN mkdir /service

COPY service/protobufs/ /service/protobufs
COPY service/snake-server/ /service/snake-server

RUN python -m pip install --upgrade pip
RUN python -m pip install grpcio
RUN python -m pip install grpcio-tools
RUN python -m pip install mysql.connector

WORKDIR /service/snake-server

EXPOSE 50051
ENTRYPOINT ["python", "server.py"]