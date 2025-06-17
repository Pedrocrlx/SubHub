compose: 
	docker compose up

build:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

up-frontend:
	docker compose up frontend

frontend-build:
	docker compose up --build frontend

