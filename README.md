# SubHub

## Project Description

**SubHub** is a secure and minimalistic application designed to help users manage their online subscriptions. It provides visibility over recurring expenses and encourages more responsible financial decisions.

## Project Objective

This application enables users to:
- Monitor and organize their active subscriptions.
- Automatically calculate the total monthly spending on subscriptions.
- Receive notifications prior to renewal dates.

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

## API Endpoints

## Environment variables (.env) example

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

4. **.env file**  
   Create a `.env` file in the project root.

## How to Open the Project

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Open the project folder in Visual Studio Code:**
   ```bash
   code .
   ```
   
3. **Create the `.env` file:**  
   Copy the example above and save it as `.env` in the root directory.

4. **Reopen in Dev Container:**  
   In VS Code, press `Ctrl+Shift+P`, then select:  
   `Dev Containers: Reopen in Container`

5. **Start the application using Make:**
   ```bash
   make compose
   ```

   Alternatively, using Docker:
   ```bash
   docker compose up --build
   ```

Now the project should be up and running.
