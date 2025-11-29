build:
	docker compose -f infra/docker-compose.yml build --no-cache

up:
	docker compose -f infra/docker-compose.yml up -d

clean:
	docker compose -f infra/docker-compose.yml down --rmi all -v --remove-orphans

rebuild: clean build up
