VOLUMES=metaautoml_datasets metaautoml_output-autokeras metaautoml_output-sklearn
CONTAINER=controller autokeras sklearn flaml autogluon pytorch autocve
DUMMY_ARGS=-f docker-compose.yml -f docker-compose-dummy.yml

compose-up-rebuild-dummy:
	make clean ; \
	docker-compose $(DUMMY_ARGS) up --build -d ; \
	docker exec -it dummy bash ; \
	docker-compose $(DUMMY_ARGS) kill

# runs everything in the foreground without dummy
compose-up-rebuild:
	# remove volumes from previous runs
	make clean ; \
	docker-compose up --build

compose-up:
	make clean ; \
	docker-compose up

clean:
	docker container rm $(CONTAINER) ; \
	docker volume rm $(VOLUMES)