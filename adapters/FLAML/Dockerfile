FROM --platform=linux/amd64 python:3.9.16-slim-buster AS base
EXPOSE 50056
EXPOSE 6000-6099

RUN apt-get update && apt-get install -y libgomp1 \
    && apt-get install -y git

RUN apt-get install -y build-essential gcc

COPY ./adapters/FLAML/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./adapters/FLAML .
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
ENTRYPOINT ["python", "FlamlServer.py"]
