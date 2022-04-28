FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 5002

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
COPY . /
WORKDIR /
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./


RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"
# TODO: edit the following line
ENTRYPOINT ["python", "Adapter_*.py"]