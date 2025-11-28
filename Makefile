.PHONY: help build up down logs lint test clean

IMAGE_SERVICE=ml-service:local

help:
	@echo "Targets: build up down logs lint test clean"

build:
	docker build -t $(IMAGE_SERVICE) ./service

up:
	docker-compose -f infra/docker-compose.yml up --build -d

down:
	docker-compose -f infra/docker-compose.yml down

logs:
	docker-compose -f infra/docker-compose.yml logs -f

lint:
	black --check .
	ruff check .

test:
	pytest -q

clean:
	docker-compose -f infra/docker-compose.yml down --rmi local --volumes --remove-orphans
