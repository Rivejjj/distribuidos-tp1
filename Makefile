SHELL := /bin/bash
PWD := $(shell pwd)


default: build

all:


docker-image:
	docker build -f ./rabbitmq/rabbitmq.dockerfile -t "rabbitmq:latest" .
	docker build -f ./gateway/Dockerfile -t "gateway:latest" .
	docker build -f ./book-filter/Dockerfile -t "book-filter:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	docker build -f ./decades-accumulator/Dockerfile -t "decades-accumulator:latest" .
	docker build -f ./reviews_counter_accum/Dockerfile -t "reviews_counter_accum:latest" .
	docker build -f ./sentiment_score_accumulator/Dockerfile -t "sentiment_score_accumulator:latest" .
	docker build -f ./sentiment_analyzer/Dockerfile -t "sentiment_analyzer:latest" .
	
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

up: docker-image
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up

up-nb: 
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up-nb


down:
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

logs:
	docker compose -f docker-compose-dev.yaml logs -f

.PHONY: docker-compose-logs
