FROM --platform=linux/amd64 python:3.9.11-slim-buster AS base
EXPOSE 50053

RUN python -m pip install --upgrade pip
RUN apt update && \
    apt install -y build-essential \
    && apt-get install -y git

RUN apt install -y font-manager

COPY ./adapters/MLJAR/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./adapters/MLJAR .
COPY ./adapters/Utils/Utils ./Utils
COPY ./adapters/Utils/AutoMLs ./AutoMLs
COPY ./adapters/Utils/Templates ./app-data/templates
COPY ./adapters/GRPC/Adapter ./
COPY ./controller/managers/ontology/ML_Ontology.ttl .

# this should already be created, but sometimes there is a bug in docker which causes that the directory is not copied
RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH ".:dependency-injection:AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "MljarServer.py"]
