BACKEND_CONTAINER=controller autokeras sklearn flaml gluon pytorch autocve
DUMMY_ARGS=-f docker-compose.yml -f docker-compose-dummy.yml
VOLUMES=metaautoml_datasets metaautoml_output metaautoml_output-autokeras metaautoml_output-sklearn metaautoml_output-flaml metaautoml_output-autocve metaautoml_output-gluon metaautoml_output-pytorch
FRONTEND_ARGS=-f docker-compose.yml -f docker-compose-frontend.yml

# runs the backend in the foreground
compose-up-rebuild-backend:
	# remove volumes from previous runs
	make clean-backend ; \
	docker-compose up --build

# runs the backend in the background with dummy
compose-up-rebuild-with-dummy:
	make clean-backend ; \
	docker-compose $(DUMMY_ARGS) up --build -d ; \
	docker exec -it dummy bash ; \
	docker-compose $(DUMMY_ARGS) down

# runs the backend in in the foreground with frontend
compose-up-rebuild-with-frontend:
	make clean-backend ; \
	docker-compose $(FRONTEND_ARGS) up --build

# removes containers and their volumes
clean-backend:
	docker container rm $(BACKEND_CONTAINER) ; \
	docker volume rm --force $(VOLUMES)

# remove controller image, because there are sometimes bugs that the datasets are not copied to docker, which is probably a caching issue
clean-controller-hard:
	docker container rm $(BACKEND_CONTAINER) ; \
	docker container prune ; \
	docker volume rm --force $(VOLUMES)

	docker image rm metaautoml_controller && \
	docker image prune