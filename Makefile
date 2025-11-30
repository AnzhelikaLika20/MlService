build:
	docker compose -f infra/docker-compose.yml build --no-cache

up:
	docker compose -f infra/docker-compose.yml up -d

clean:
	docker compose -f infra/docker-compose.yml down --rmi all -v --remove-orphans

create-bucket:
	docker exec -it ml_service bash -c "PYTHONPATH=/app python -m app.scripts.create_bucket"

dvc-init:
	docker exec -it ml_service bash -c "PYTHONPATH=/app python -m app.scripts.init_dvc"

rebuild: clean build up create-bucket dvc-init
