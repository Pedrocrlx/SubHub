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


## Description
**SubHub** is a simple and secure application that helps users manage their online subscriptions, providing clear visibility over recurring costs and promoting healthier financial habits.

## 🚀 Project Goal

The app allows users to:
- View and manage their active subscriptions
- Automatically calculate total monthly spending
- Receive alerts before subscription renewals

This MVP focuses on core functionality with a clean and static UI.

## 🛠️ Tech Stack

- **Frontend**: HTML + CSS and JavaScript (no frameworks)
- **Backend**: Python 3.12 + FastAPI
- **Database**: PostgreSQL
- **Containers**: Docker + Docker Compose
- **Development Environment**: VSCode DevContainer
- **Dependency Management**: Poetry
- **Version Control**: Git + GitHub

## ✨ Features

- User authentication and authorization.
- Subscription tracking and management.
- RESTful API for backend services.
- Responsive frontend served via NGINX.
- Containerized architecture for seamless deployment.

## 📂 Project Structure
```
SubHub/
├── backend/          # Backend service (FastAPI)
├── frontend/         # Frontend service (NGINX)
├── docs/             # Documentation files
├── compose.yaml      # Docker Compose
├── LICENSE           # MIT license
├── Makefile          # Makefile with commands
└── README.md         # Project overview
```

## ⚙️ How to Run the Project
```bash
docker compose up --build
```

This will spin up:

- The FastAPI backend (`localhost:8000`)
- The Nginx frontend (`localhost:3000`)
- PostgreSQL database
- Adminer DB UI (`localhost:8080`)

---

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, JWT, bcrypt
- **Frontend:** Nginx serving static HTML
- **Database:** PostgreSQL
- **Admin Interface:** Adminer

---
or (Makefile option)

```bash
make compose
```

## 📌 MVP Notes

- User authentication is not included in this version.
- Services must be added manually by the user (future integration with APIs planned).

## 👥 Team

- Pedro Santos — Backend architecture, Docker/DevOps
- Giulio & Nuno — Backend development
- Nelson — Frontend implementation
