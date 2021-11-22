FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 5006

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt

RUN git clone git@github.com:celiolarcher/AUTOCVE.git
RUN cd AUTOCVE
RUN pip install -r requirements.txt
RUN pip install .
RUN cd ..

COPY . /
WORKDIR /

VOLUME ["/app-data"]
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "/AutoMLs:/templates:/templates/output"
ENTRYPOINT ["python", "Adapter_AutoCVE.py"]