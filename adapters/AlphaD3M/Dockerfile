FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 50060

# Install dependencies
COPY ./AlphaD3M/requirements.txt .

# Have to install these dependencies before the requirements.txt,
#   because inside the requirements.txt the packages/modules are installed out of order.
RUN pip install d3m
RUN pip install numpy

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
# TODO: edit the following line
ENTRYPOINT ["python", "Adapter_AlphaD3M.py"]