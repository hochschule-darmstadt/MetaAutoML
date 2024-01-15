.PHONY: all

all:
    docker-compose -f docker-compose.yml -f docker-compose-frontend.yml up


