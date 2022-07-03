FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 5001

COPY ./controller/requirements.txt .
# Install dependencies
RUN apt update
RUN apt install -y git
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./controller .
COPY ./adapters/GRPC/Adapter ./
COPY ./adapters/GRPC/Controller ./
COPY ./adapters/Utils/Utils ./utils
# set all environment variables that are valid for docker-compose and kubernetes
# all specific enviraonment variables shall then be set by docker or cubernetes when starting the container
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "interfaces:managers:managers/adaptermanagers:sessions:utils"
ENV RUNTIME=DOCKER
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "Controller.py"]
