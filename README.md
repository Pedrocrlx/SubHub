# SubHub

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