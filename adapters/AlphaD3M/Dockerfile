FROM python:3.8.13-slim-buster AS base
WORKDIR /
EXPOSE 50060

# Install C/C++ Build environment
RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get install -y g++

# Install dependencies
COPY ./AlphaD3M/requirements.txt .
RUN pip install d3m==2022.5.5 numpy==1.19.5
RUN pip install -r requirements.txt
WORKDIR /app
COPY ./AlphaD3M .
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./


RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"

ENTRYPOINT ["python", "AlphaD3MServer.py"]