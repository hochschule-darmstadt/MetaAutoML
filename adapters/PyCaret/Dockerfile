FROM --platform=linux/amd64 python:3.11.7-slim-bullseye AS base
EXPOSE 50056

RUN apt-get update && apt-get install -y libgomp1 \
    && apt-get install -y git && apt-get install -y gcc

COPY ./adapters/PyCaret/requirements.txt .
# Install dependencies
RUN pip install "cython<3.0.0" && pip install --no-build-isolation pyyaml==5.4.1
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./adapters/PyCaret .
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
ENTRYPOINT ["python", "PyCaretServer.py"]
