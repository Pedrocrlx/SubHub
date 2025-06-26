
# Docker & Dev Environment

This section documents how to configure and run the complete development environment for the project using Docker, including both backend and frontend services.

---

## 1. Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.12

RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- Base image: `python:3.12`
- Poetry installation and dependency management
- Exposes port 8000 for FastAPI server
- Starts FastAPI using `uvicorn`

---

## 2. Frontend Dockerfile with Nginx

```dockerfile
# frontend/Dockerfile
FROM nginx:1.27

# Copy the built frontend files to the nginx html directory
COPY ./html /usr/share/nginx/html
COPY ./conf.d/ /etc/nginx/conf.d/

EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

- Nginx image for static content
- Exposes port 3000

---

## 3. compose.yml

```yaml
services:
  backend:
    build:
      dockerfile: Dockerfile
      context: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    networks:
      - my-app-net

  frontend:
    build:
      dockerfile: Dockerfile
      context: ./frontend
    ports:
      - "3000:3000" # Port 3000 is not the default for NGINX; it was changed using custom configuration files in conf.d.
    volumes:
      - ./frontend/html:/usr/share/nginx/html
      - ./frontend/conf.d/:/etc/nginx/conf.d/ # Nginx configuration files to change the default port 80 to 3000:3000.
    networks:
      - my-app-net
  
  db:
    image: postgres:17
    ports:
      - 5432:5432
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: qwerty
      POSTGRES_DB: subHub
    networks:
      - my-app-net

  adminer:
    image: adminer:latest
    ports:
      - 8080:8080

networks: # Define a custom network for the services to communicate.
  my-app-net:
    driver: bridge
```

- Orchestrates backend, frontend, and database services
- Enables container intercommunication
- Uses volumes for persistent PostgreSQL data

---

## 4. .devcontainer for VSCode

- References the backend Dockerfile
- Allows project to be opened directly in container

---

## 5. .dockerignore

Example:

```
__pycache__/
*.pyc
.env
.git
```

- Prevents unnecessary files from being included in Docker builds

---

## 6. Usage

- **Build backend manually:** `docker build -f backend/Dockerfile -t subhub-backend .`
- **Run entire stack:** `docker compose up --build`
- **Run specific service:** `docker compose up <service> --build`
- **Access frontend:** `http://localhost:3000`
- **Access backend:** `http://localhost:8000`
- **Access Adminer:** `http://localhost:8080`