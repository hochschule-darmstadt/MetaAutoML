FROM --platform=linux/amd64 python:3.9.13-slim-buster AS base
EXPOSE 50062

RUN apt-get update && apt-get install -y git && apt-get install libgomp1

RUN apt-get install -y build-essential gcc
COPY ./adapters/EvalML/requirements.txt .
#COPY ./EvalML/core-requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
#RUN pip install -r core-requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./adapters/EvalML .
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
ENTRYPOINT ["python", "EvalMLServer.py"]
