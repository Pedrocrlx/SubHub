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