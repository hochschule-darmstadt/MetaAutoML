FROM python:3.7.11-slim-buster AS base
EXPOSE 50058

RUN python -m pip install --upgrade pip
RUN apt update && \
    apt install -y git

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt

# install autocve from source
RUN git clone https://github.com/celiolarcher/AUTOCVE.git && \
    cd AUTOCVE && \
    pip install -r requirements.txt && \
    pip install .

WORKDIR /app
COPY . .

ENV RUNTIME=DOCKER
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "AutoMLs:Utils"
ENV PYTHON_ENV "python"
ENTRYPOINT ["python", "Adapter_AutoCVE.py"]