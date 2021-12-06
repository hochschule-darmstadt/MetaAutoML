start-compose:
	# remove volumes from previous runs
	docker container rm controller autokeras sklearn flaml autogluon pytorch autocve ; \
	docker volume rm metaautoml_output ; \
	docker volume rm metaautoml_datasets ; \
	docker-compose up --build