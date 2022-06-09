FROM python:3.7.11-slim-buster AS base
EXPOSE 50055

COPY ./AutoSklearn/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY ./AutoSklearn .
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./

# this should already be created, but sometimes there is a bug in docker which causes that the directory is not copied
RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "AutoSklearnServer.py"]