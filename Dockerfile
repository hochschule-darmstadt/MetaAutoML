FROM python:3.7.11-slim-buster AS base
WORKDIR /
EXPOSE 5001

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
COPY . /
WORKDIR /

# set all environment variables that are valid for docker-compose and kubernetes
# all specific enviraonment variables shall then be set by docker or cubernetes when starting the container
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH "/interfaces:/managers:/managers/structureddata:/sessions:/utils"
ENV RUNTIME=1
ENTRYPOINT ["python", "Controller.py"]