FROM --platform=linux/amd64  python:3.9.13-slim-buster AS base
EXPOSE 50057

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libquadmath0 \
    ffmpeg \
    libsm6 \
    libxext6  \
    gcc \
    && apt-get install -y git

RUN python3 -m pip install --upgrade "mxnet<2.0.0"

COPY ./adapters/AutoGluon/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./adapters/AutoGluon .
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
ENTRYPOINT ["python", "AutoGluonServer.py"]
