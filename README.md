# SubHub
Subscription Management

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/subhub.git
cd subhub
```

### 2. Configure Environment Variables

This project uses a `.env` file to manage secrets and configuration. For security reasons, the real `.env` file is **not included** in version control.

1. Copy the example file:

    ```bash
    cp .env.example .env
    ```

2. Open `.env` in a text editor and fill in the values:

    ```dotenv
    # .env

    SECRET_KEY=your_secure_jwt_secret
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=qwerty
    POSTGRES_DB=subHub
    ```

   > To generate a secure SECRET_KEY (on macOS/Linux):
   > ```bash
   > openssl rand -hex 32
   > ```

### 3. Run the Application with Docker

Ensure Docker is installed and running on your machine.


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
- **VSCode DevContainer** – Facilitates a pre-configured development environment for all contributors.
- **Poetry** – Manages Python dependencies and virtual environments in a reproducible and maintainable way.
- **Git and GitHub** – Used for version control, collaboration, and continuous integration.

## Key Features

- Secure user authentication and basic authorization.
- Manual subscription management interface.
- RESTful API endpoints for communication between frontend and backend.
- Static frontend hosted through an NGINX container.
- Fully containerized architecture for cross-platform compatibility.

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


## Running the Project

To build and start the application, run:

```bash
docker compose up --build
```

Alternatively, using Makefile:

```bash
make compose
```

## Development Team

- **Pedro Santos** – Backend architecture and Docker/DevOps lead
- **Giulio & Nuno** – Backend implementation
- **Nelson** – Frontend development
