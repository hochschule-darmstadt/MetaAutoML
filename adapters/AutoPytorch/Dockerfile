FROM --platform=linux/amd64 python:3.9.16-slim-buster AS base
EXPOSE 50059

RUN apt-get update && apt-get install -y git

RUN python -m pip install --upgrade pip

COPY ./adapters/AutoPytorch/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app

# libs required by the automl
RUN apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6

WORKDIR /app
COPY ./adapters/AutoPytorch .
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
ENTRYPOINT ["python", "AutoPytorchServer.py"]
