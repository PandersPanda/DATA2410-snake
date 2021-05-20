FROM python

RUN mkdir /service

COPY service/protobufs/ /service/protobufs
COPY service/snake-server/ /service/snake-server

WORKDIR /service/snake-server
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirement.txt

EXPOSE 50051
ENTRYPOINT ["python", "server.py"]