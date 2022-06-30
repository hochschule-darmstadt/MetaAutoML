FROM python:3.8.13 AS base
WORKDIR /
EXPOSE 50060

# Install C/C++ Build environment
RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get install -y g++

# Upgrade pip
RUN python -m pip install --upgrade pip

# Install dependencies
WORKDIR /app
COPY ./AlphaD3M/requirements.alphad3m.txt ./AlphaD3M/requirements.primitives.txt ./AlphaD3M/requirements.txt ./
RUN pip install -r requirements.alphad3m.txt
RUN pip install -r requirements.primitives.txt
RUN pip install -r requirements.txt

# Copy code
COPY ./AlphaD3M .
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./

# Setup runtime
RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"

ENTRYPOINT ["python", "AlphaD3MServer.py"]