build:
	docker compose -f infra/docker-compose.yml build

up:
	docker compose -f infra/docker-compose.yml up -d

clean:
	docker compose -f infra/docker-compose.yml down --rmi all -v --remove-orphans

create-bucket:
	docker exec -it ml_service bash -c "PYTHONPATH=/app python -m app.scripts.create_bucket"

dvc-init:
	docker exec -it ml_service bash -c "PYTHONPATH=/app python -m app.scripts.init_dvc"

rebuild: build up create-bucket dvc-init

# MINIKUBE_DRIVER ?= docker

# setup-kubectl:
# 	@if ! command -v kubectl &> /dev/null; then \
# 		echo "Installing kubectl..."; \
# 		curl -LO "https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/$(shell uname | tr '[:upper:]' '[:lower:]')/amd64/kubectl"; \
# 		chmod +x ./kubectl; \
# 		sudo mv ./kubectl /usr/local/bin/; \
# 	else \
# 		echo "kubectl already installed"; \
# 	fi
# 	@if ! command -v minikube &> /dev/null; then \
# 		echo "Please install Minikube from https://minikube.sigs.k8s.io/docs/start/"; \
# 	fi

# build:
# 	docker build -t ml-service:latest    -f service/Dockerfile service
# 	docker build -t dashboard:latest     -f dashboard/Dockerfile dashboard
# 	docker build -t grpc-client:latest   -f grpc_client/Dockerfile grpc_client

# push:
# 	eval $$(minikube docker-env); \
# 	docker build -t ml-service:latest    -f service/Dockerfile service; \
# 	docker build -t dashboard:latest     -f dashboard/Dockerfile dashboard; \
# 	docker build -t grpc-client:latest   -f grpc_client/Dockerfile grpc_client

# minikube-start:
# 	minikube start --driver=$(MINIKUBE_DRIVER)

# k8s-deploy:
# 	kubectl apply -f deploy/minio.yaml
# 	kubectl apply -f deploy/pvc.yaml
# 	kubectl apply -f deploy/api.yaml
# 	kubectl apply -f deploy/dashboard.yaml
# 	kubectl apply -f deploy/grpc.yaml

# open-dashboard:
# 	minikube service dashboard

# open-api:
# 	minikube service ml-service

# all: minikube-start push k8s-deploy

# stop:
# 	minikube stop

# clean:
# 	minikube delete
