# SubHub

## Project Description

**SubHub** is a secure and minimalistic application designed to help users manage their online subscriptions. It provides visibility over recurring expenses and encourages more responsible financial decisions.

## Project Objective

This application enables users to:
- Monitor and organize their active subscriptions.
- Automatically calculate the total monthly spending on subscriptions.

This MVP focuses on delivering essential functionality with a static, user-friendly interface.

## Technology Stack

- **HTML, CSS, JavaScript (Vanilla)** – Used for building a lightweight, static frontend without additional framework complexity.
- **Python 3.12** – A modern, widely supported programming language suitable for backend services.
- **FastAPI ^0.115.0** – A high-performance web framework for building RESTful APIs quickly and with automatic documentation.
- **PostgreSQL 17** – A robust, open-source relational database system ideal for managing structured data securely.
- **NGINX 1.27** – Used to serve the static frontend content efficiently in a production environment.
- **Docker** – Provides isolated containers for each service to ensure consistent environments across development and deployment.
- **Docker Compose** – Simplifies the orchestration and management of multi-container applications.
- **VSCode DevContainer - Docker in Docker** – Facilitates a pre-configured development environment for all contributors.
- **Poetry** – Manages Python dependencies and virtual environments in a reproducible and maintainable way.
- **Git and GitHub** – Used for version control, collaboration, and continuous integration.

## Key Features

- Secure user authentication and basic authorization.
- Manual subscription management interface.
- RESTful API endpoints for communication between frontend and backend.
- Static frontend hosted through an NGINX container.
- Fully containerized architecture for cross-platform compatibility.

## Environment variables (.env) example:
```
SECRET_KEY=your_secret_key_here
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=subHub  
```

## Project Structure
```
SubHub/
├── backend/          # FastAPI application code
├── frontend/         # Static frontend assets served via NGINX
├── docs/             # Project and technical documentation
├── compose.yaml      # Docker Compose configuration file
├── LICENSE           # MIT license
├── Makefile          # Command shortcuts
└── README.md         # Project overview and setup instructions
```

## Architecture Diagram

![Architecture diagram](docs\architecture-diagram.png)

## Prerequisites

Before opening the project, make sure you have the following installed:

1. **Visual Studio Code**  
   Download and install from: https://code.visualstudio.com/

2. **VS Code Extensions**  
   In Visual Studio Code, install the following extensions:
   - Docker
   - Dev Containers

3. **Docker Desktop**  
   Download and install from: https://www.docker.com/products/docker-desktop/

4. **.env file** (#how-to-open-the-project)
   Create a `.env` file in the project root and use the variables used in .env.example.

## How to Open the Project

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/Pedrocrlx/SubHub.git>
   cd <SubHub>
   ```

2. **Open the project folder in Visual Studio Code:**
   ```bash
   code .
   ```

3. **Reopen in Dev Container:**  
   In VS Code, press `Ctrl+Shift+P`, then select:  
   `Dev Containers: Reopen in Container`

4. **Install dependencies**
   Go to /workspaces/SubHub/backend and run.
   ```bash
   poetry install
   ```
   
5. **Start the application using Make:**
   ```bash
   make compose
   ```

   Alternatively, using Docker:
   ```bash
   docker compose up
   ```

   You can check all the make commands running:
   ```bash
   make help
   ```

Now the project should be up and running.
