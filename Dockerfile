FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 5001

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
COPY . /
WORKDIR /

VOLUME ["/app-data"]
ENV PYTHONUNBUFFERED=0
ENV PYTHONPATH "/AutoMLs:/templates:/templates/output"
ENTRYPOINT ["python", "Controller.py"]