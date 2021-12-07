FROM python:3.7.11-slim-buster AS base
EXPOSE 50052

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY . .

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "Adapter_AutoKeras.py"]