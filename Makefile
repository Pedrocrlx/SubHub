.PHONY: help

help: ## Show this help message and exit
    @echo "Available commands:"
    @grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
        awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services defined in compose.yml without rebuilding
	@echo "Starting all services defined in compose.yml..."
	docker compose up

compose: build ## Start all services defined in compose.yml
	@echo "Starting all services defined in compose.yml..."
	@echo "Use 'make up' to start services without rebuilding."
	docker compose up

build:
	@echo "Building all services..."
	docker compose up --build

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

