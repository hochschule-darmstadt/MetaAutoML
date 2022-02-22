FROM python:3.7.11-slim-buster AS base

COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# put all files in a directory called app
WORKDIR /app
COPY . .

# set all environment variables that are valid for docker-compose and kubernetes
# all specific envirvonment variables shall then be set by docker or cubernetes when starting the container
ENV PYTHONUNBUFFERED=1
# just do nothing, we will than get an interactive shell using docker exec -it
ENTRYPOINT ["bash", "./sleep.sh"]
