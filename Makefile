.PHONY:help 

help:       
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

up: ## Start all services defined in compose.yml without rebuilding
	@echo "Starting all services defined in compose.yml..."
	docker compose up

compose: ## Start all services defined in compose.yml
	@echo "Starting all services defined in compose.yml..."
	@echo "Use 'make up' to start services without rebuilding."
	docker compose up

build:
	@echo "Building all services..."
	docker compose up --build --force-recreate

down: ## Stop and remove all containers
	@echo "Stopping and removing all containers..."
	docker compose down

logs: ## Show logs from all containers
	@echo "Showing logs from all containers..."
	docker compose logs -f

up-frontend: ## Start the frontend service
	@echo "Starting frontend service..."
	docker compose up frontend

frontend-build: ## Build the frontend service
	@echo "Building frontend service..."
	docker compose up --build frontend

prune: ## Delete all containers
	docker system prune -a