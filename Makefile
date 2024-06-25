SHELL := /bin/bash
PWD := $(shell pwd)

default: build

all:

docker-image:
	docker build -f ./monitor/Dockerfile -t "monitor:latest" .
	docker build -f ./gateway/Dockerfile -t "gateway:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	docker build -f ./data_processors/book_filter/Dockerfile -t "book_filter:latest" .
	docker build -f ./data_processors/decades_accumulator/Dockerfile -t "decades_accumulator:latest" .
	docker build -f ./data_processors/top_rating_accumulator/Dockerfile -t "top_rating_accumulator:latest" .
	docker build -f ./data_processors/reviews_counter_accum/Dockerfile -t "reviews_counter_accum:latest" .
	docker build -f ./data_processors/sentiment_score_accumulator/Dockerfile -t "sentiment_score_accumulator:latest" .
	docker build -f ./data_processors/sentiment_analyzer/Dockerfile -t "sentiment_analyzer:latest" .
	
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

up: docker-image
	# sudo rm -rf data/query
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up

up-nb: 
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up-nb

rmq-up: 
	docker build -f ./rabbitmq/rabbitmq.dockerfile -t "rabbitmq:latest" .
	docker compose -f docker-compose-rmq.yaml up --build
.PHONY: docker-compose-rmq-up

rmq-down: 
	docker compose -f docker-compose-rmq.yaml stop -t 1
	docker compose -f docker-compose-rmq.yaml down
.PHONY: docker-compose-rmq-down

down:
	docker compose -f docker-compose-dev.yaml stop -t 5
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

logs:
	docker compose -f docker-compose-dev.yaml logs -f

.PHONY: docker-compose-logs
