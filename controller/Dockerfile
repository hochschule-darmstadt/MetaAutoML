FROM python:3.9.13-slim-buster AS base
WORKDIR /
EXPOSE 5001

# git is required for installing pip requirements
#  python-betterproto is cloned from github 
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -qq install \
    git gcc

COPY ./controller/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./controller .
COPY ./adapters/Utils/Utils ./utils
# set all environment variables that are valid for docker-compose and kubernetes
# all specific enviraonment variables shall then be set by docker or cubernetes when starting the container
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "blackboard:blackboard/agents:blackboard/strategies:dependency-injection:interfaces:managers:managers/adapter/online_prediction:managers/adapter:managers/analysis:managers/data:managers/general:managers/ontology:persistence:utils"
ENV RUNTIME=DOCKER
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "ControllerServer.py"]