FROM --platform=linux/amd64 python:3.7.11-slim-buster AS base
EXPOSE 50061

RUN apt-get update && apt-get install -y libgomp1 \
    && apt-get install -y git 

COPY ./FLAML/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./EvalML .
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./

# this should already be created, but sometimes there is a bug in docker which causes that the directory is not copied
RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH ".:dependency-injection:AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "EvalMLServer.py"]