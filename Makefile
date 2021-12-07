VOLUMES=metaautoml_output metaautoml_datasets
CONTAINER=controller autokeras sklearn flaml autogluon pytorch autocve
DUMMY_ARGS=-f docker-compose.yml -f docker-compose-dummy.yml

compose-up-build-dummy:
	make clear ; \
	docker-compose $(DUMMY_ARGS) up --build -d ; \
	docker exec -it dummy bash ; \
	docker-compose $(DUMMY_ARGS) kill

compose-up-build:
	# remove volumes from previous runs
	make clear ; \
	docker-compose up --build

clear:
	docker container rm $(CONTAINER) ; \
	docker volume rm $(VOLUMES)