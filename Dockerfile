FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 5001

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
COPY . /
WORKDIR /

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "/interfaces:/managers:/managers/structureddata:/sessions"
ENTRYPOINT ["python", "Controller.py"]