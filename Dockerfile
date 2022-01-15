FROM python:3.7.11-slim-buster AS base
EXPOSE 50057

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libquadmath0

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY . .

# this should already be created, but sometimes there is a bug in docker which causes that the directory is not copied
RUN mkdir -p /app/app-data/output/tmp

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "Adapter_AutoGluon.py"]