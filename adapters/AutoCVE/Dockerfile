FROM python:3.6-slim-buster AS base
EXPOSE 50058

RUN apt-get update && \
    apt-get install -y gcc && \
    apt-get install -y g++ && \
    apt-get install -y git
#

RUN python -m pip install --upgrade pip

# numpy has to be installed before the requirements because for the remote source from git (for AutoCVE) to work it has
# to be installed already. Apperantly pip does not install requrements.txt files in order.
RUN pip install numpy==1.19.5

COPY ./AutoCVE/requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt

WORKDIR /app
COPY ./AutoCVE .
COPY ./Utils/Utils ./Utils
COPY ./Utils/AutoMLs ./AutoMLs
COPY ./GRPC/Adapter ./

# this should already be created, but sometimes there is a bug in docker which causes that the directory is not copied
RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "Adapter_AutoCVE.py"]