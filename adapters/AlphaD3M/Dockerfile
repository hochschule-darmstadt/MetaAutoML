FROM python:3.8.13-slim-buster AS base
WORKDIR /
EXPOSE 50060

# Install C/C++ Build environment
RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get install -y g++

RUN python -m pip install --upgrade pip

# Copy code
WORKDIR /app
COPY ./AlphaD3M .
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./

# Install dependencies
RUN pip install -r requirements.alphad3m.txt
RUN pip install -r requirements.primitives.txt
RUN pip install -r requirements.txt


RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"

ENTRYPOINT ["python", "AlphaD3MServer.py"]