FROM python:3.7.11-slim-buster AS base
EXPOSE 50059

RUN python -m pip install --upgrade pip

COPY ./AutoPytorch/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app

# libs required by the automl
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6

WORKDIR /app
COPY ./AutoPytorch .
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./

# this should already be created, but sometimes there is a bug in docker which causes that the directory is not copied
RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "Adapter_AutoPyTorch.py"]