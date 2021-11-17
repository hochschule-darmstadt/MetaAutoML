FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 5002

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
COPY . /
WORKDIR /

VOLUME ["/app-data"]
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "/AutoMLs:/templates:/templates/output:/Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "Adapter_Autosklearn.py"]