CONTAINER=controller autokeras sklearn flaml autogluon pytorch autocve
DUMMY_ARGS=-f docker-compose.yml -f docker-compose-dummy.yml
VOLUMES=metaautoml_datasets metaautoml_output metaautoml_output-autokeras metaautoml_output-sklearn metaautoml_output-flaml

compose-up-rebuild-dummy:
	make clean ; \
	docker-compose $(DUMMY_ARGS) up --build -d ; \
	docker exec -it dummy bash ; \
	docker-compose $(DUMMY_ARGS) down

# runs everything in the foreground without dummy
compose-up-rebuild:
	# remove volumes from previous runs
	make clean ; \
	docker-compose up --build

compose-up:
	make clean ; \
	docker-compose up

clean:
	# remove containers and their volumes
	docker container rm $(CONTAINER) ; \
	docker volume rm --force $(VOLUMES)

# remove controller image, because there are sometimes bugs that the datasets are not copied to docker, which is probably a caching issue
clean-controller-hard:
	make clean && \
	docker image rm metaautoml_controller && \
	docker image prune