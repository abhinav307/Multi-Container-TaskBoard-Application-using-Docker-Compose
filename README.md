# Multi-Container-TaskBoard-Application-using-Docker-Compose

[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-v2.x-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16--Alpine-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.12--Slim-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gunicorn](https://img.shields.io/badge/WSGI-Gunicorn-499848?logo=gunicorn&logoColor=white)](https://gunicorn.org/)

> **Program 14 — Cloud Computing & DevOps Lab**  
> A multi-container web application consisting of a **Python Flask web service** and a **PostgreSQL 16 database** orchestrated using **Docker Compose**. Supports full CRUD task tracking, automated health checks, inter-service networking, and persistent data storage through Docker named volumes.

---

## 📑 Table of Contents

- [Overview & Aim](#-overview--aim)
- [Architecture & Multi-Tier Design](#-architecture--multi-tier-design)
- [Project Directory Structure](#-project-directory-structure)
- [Prerequisites & System Requirements](#-prerequisites--system-requirements)
- [Environment Configuration](#-environment-configuration)
- [How to Build and Run](#-how-to-build-and-run)
- [Service Verification & Testing](#-service-verification--testing)
  - [Container Status](#1-container-status)
  - [Healthcheck Verification](#2-healthcheck-verification)
  - [Database Inspection](#3-database-inspection)
- [Data Persistence Testing (Volume Durability)](#-data-persistence-testing-volume-durability)
- [Docker Compose Configuration Reference](#-docker-compose-configuration-reference)
- [Key Architectural Concepts](#-key-architectural-concepts)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [Resource Teardown & Cleanup](#-resource-teardown--cleanup)
- [GitHub Setup & Push Guide](#-github-setup--push-guide)

---

## 🎯 Overview & Aim

The goal of this project is to build, package, and orchestrate a multi-container web application using **Docker Compose**:

1. **Flask Application (`web`)**: A Python-based responsive web app serving a dynamic TaskBoard interface via Jinja2 templates and vanilla CSS. Runs production-grade WSGI through `gunicorn` with multiple workers.
2. **PostgreSQL Database (`db`)**: A robust relational database (`postgres:16-alpine`) storing tasks, completion states, and timestamps.
3. **Data Persistence**: Backed by a Docker **named volume** (`taskboard_data`) so data persists across container restarts, teardowns, and rebuilds.
4. **Service Healthchecks & Orchestration**: Uses Docker Compose `depends_on` with `condition: service_healthy` to guarantee Flask only initializes after PostgreSQL is accepting connections.
5. **Isolated Bridge Networking**: Services communicate over an internal private bridge network (`taskboard_net`). The database port (`5432`) is hidden from the host machine for security.

---

## 🏗 Architecture & Multi-Tier Design

```
+---------------------------------------------------------------------------------+
|                                 Host Machine                                    |
|                                                                                 |
|   Browser / HTTP Client                                                         |
|         │                                                                       |
|         ▼ (Port 8081)                                                           |
|  +---------------------------------------------------------------------------+  |
|  |                            Docker Engine                                  |  |
|  |                                                                           |  |
|  |   +────────────────── taskboard_net (Bridge Network) ─────────────────+   |  |
|  |   │                                                                   │   |  |
|  |   │    +──────────────────────+              +───────────────────+    │   |  |
|  |   │    |     web service      |              |    db service     |    │   |  |
|  |   │    |   (Flask/Gunicorn)   |              |  (PostgreSQL 16)  |    │   |  |
|  |   │    |                      |  psycopg/TCP |                   |    │   |  |
|  |   │    |  Container Port: 5000│─────────────>│ Host: db          |    │   |  |
|  |   │    |  Health: /health     |  Port: 5432  | Port: 5432        |    │   |  |
|  |   │    +──────────────────────+              +─────────┬─────────+    │   |  |
|  |   │                                                    │              │   |  |
|  |   +────────────────────────────────────────────────────┼──────────────+   |  |
|  |                                                        │                  |  |
|  |                                                        ▼                  |  |
|  |                                            +───────────────────────+      |  |
|  |                                            |     Named Volume      |      |  |
|  |                                            |    taskboard_data     |      |  |
|  |                                            | (/var/lib/postgresql) |      |  |
|  |                                            +───────────────────────+      |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
```

---

## 📁 Project Directory Structure

```text
Multi-Container-TaskBoard-Application-using-Docker-Compose/
├── .env                          # Local environment secrets (auto-generated from .env.example)
├── .env.example                  # Template configuration for database & application credentials
├── .gitignore                    # Prevents secrets (.env), caches, and virtual environments from git
├── Dockerfile                    # Multi-stage Python 3.12-slim build definition with Gunicorn
├── README.md                     # Comprehensive technical documentation & runbook
├── app.py                        # Flask application source code, database connector & health route
├── compose.yaml                  # Declarative Docker Compose specification (web, db, network, volume)
├── requirements.txt              # Pinned Python package dependencies (Flask, Gunicorn, psycopg)
├── static/
│   └── styles.css                # Responsive UI styling, status badges, and typography
└── templates/
    └── index.html                # Jinja2 template for TaskBoard interface and flash notifications
```

---

## ⚙️ Prerequisites & System Requirements

Ensure the following tools are installed and operational:

- **Windows 10/11**, **macOS**, or **Linux**
- **Docker Desktop** (with the Docker Compose v2 plugin enabled)
- A modern web browser

Verify Docker and Docker Compose versions:

```powershell
docker --version
docker compose version
```

---

## 🔐 Environment Configuration

The application uses an `.env` file to securely inject database credentials into both the `db` and `web` containers.

Create your `.env` file by copying the template:

```powershell
Copy-Item .env.example .env
```

Default demo values in `.env`:

```env
POSTGRES_DB=taskboard
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpass
FLASK_SECRET_KEY=local-demo-change-this-key
```

> [!NOTE]  
> The `.env` file is excluded from version control via `.gitignore` to prevent credential leakage.

---

## 🚀 How to Build and Run

From the project root directory, launch the entire stack:

```powershell
docker compose up -d --build
```

### What happens under the hood:
1. **Network Creation**: Creates `taskboard_net` bridge network.
2. **Volume Allocation**: Allocates persistent storage volume `taskboard_data`.
3. **Database Pull & Initialization**: Pulls `postgres:16-alpine`, starts the PostgreSQL daemon, and executes health probes (`pg_isready`).
4. **Application Build**: Builds the Flask container from `Dockerfile` installing dependencies from `requirements.txt`.
5. **Dependency Wait**: Waits for PostgreSQL to report healthy before starting the `web` container.
6. **Port Mapping**: Exposes container port `5000` to host port `8081`.

### Accessing the Application

Open your browser and navigate to:

👉 **`http://localhost:8081`**

---

## 🔍 Service Verification & Testing

### 1. Container Status

Check the status of both running services:

```powershell
docker compose ps
```

Expected output:
```text
NAME                                                        IMAGE                         COMMAND                  SERVICE   CREATED          STATUS                    PORTS
multi-container-taskboard-application-using-docker-compose-db-1    postgres:16-alpine            "docker-entrypoint.s…"   db        About a minute   Up (healthy)              5432/tcp
multi-container-taskboard-application-using-docker-compose-web-1   multi-container...-web        "gunicorn --bind 0.0…"   web       About a minute   Up (healthy)              0.0.0.0:8081->5000/tcp
```

### 2. Healthcheck Verification

Query the Flask application's `/health` endpoint:

```powershell
Invoke-RestMethod http://localhost:8081/health
```

Expected JSON response:
```json
{
  "database": "connected",
  "status": "healthy"
}
```

### 3. Database Inspection

Query the PostgreSQL database directly through `docker compose exec`:

```powershell
docker compose exec db psql -U taskuser -d taskboard -c "SELECT id, title, completed, created_at FROM tasks ORDER BY id;"
```

---

## 💾 Data Persistence Testing (Volume Durability)

To verify that the database data survives container recreation:

1. Open `http://localhost:8081` in your browser.
2. Add tasks (e.g., *"Complete DevOps Lab"*, *"Review Docker Compose"*).
3. Stop and destroy the containers (without deleting the named volume):
   ```powershell
   docker compose down
   ```
4. Restart the containers:
   ```powershell
   docker compose up -d
   ```
5. Refresh `http://localhost:8081`. Notice all previously inserted tasks remain completely intact because PostgreSQL stored them in the `taskboard_data` volume.

---

## 📄 Docker Compose Configuration Reference

The complete `compose.yaml` file orchestrating the multi-container stack:

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-taskboard}
      POSTGRES_USER: ${POSTGRES_USER:-taskuser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-taskpass}
    volumes:
      - taskboard_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 12
    networks:
      - taskboard_net

  web:
    build: .
    restart: unless-stopped
    environment:
      DB_HOST: db
      DB_PORT: 5432
      POSTGRES_DB: ${POSTGRES_DB:-taskboard}
      POSTGRES_USER: ${POSTGRES_USER:-taskuser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-taskpass}
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY:-local-demo-change-this-key}
    ports:
      - "8081:5000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)"]
      interval: 10s
      timeout: 4s
      retries: 5
      start_period: 15s
    networks:
      - taskboard_net

volumes:
  taskboard_data:

networks:
  taskboard_net:
    driver: bridge
```

---

## 💡 Key Architectural Concepts

| Concept | Implementation Details |
| :--- | :--- |
| **Multi-Container Architecture** | Decouples the presentation/application logic (`web`) from the stateful database tier (`db`), allowing independent scaling and lifecycle management. |
| **Declarative Orchestration** | Defined in `compose.yaml`; eliminates manual `docker run` commands and flags. |
| **Service Dependency (`depends_on`)** | Uses `condition: service_healthy` rather than merely waiting for container start, eliminating race conditions during cold database boot. |
| **Healthchecks** | `pg_isready` verifies database engine readiness; Python URL opener validates HTTP status `200` on `/health`. |
| **Network Isolation** | Both containers join `taskboard_net`. The database container communicates over internal port 5432 without exposing any host port. |
| **Storage Persistence** | Docker managed named volume `taskboard_data` preserves database files outside container ephemeral storage. |

---

## 🛠 Troubleshooting & FAQs

### Port 8081 is already in use
If another application or previous container is using port 8081:
```powershell
Get-NetTCPConnection -LocalPort 8081
```
You can edit the `ports` mapping in `compose.yaml` (e.g., `"8082:5000"`) and rerun `docker compose up -d`.

### View Container Logs
If a service fails to start or reports unhealthy:
```powershell
# View web logs
docker compose logs web

# View db logs
docker compose logs db

# Stream both in real time
docker compose logs -f
```

### Force Image Rebuild
To rebuild the Flask application image from scratch after modifying code or requirements:
```powershell
docker compose build --no-cache
docker compose up -d
```

---

## 🧹 Resource Teardown & Cleanup

### Normal Teardown (Preserving Data)
Stops and removes containers and networks while keeping your saved tasks:
```powershell
docker compose down
```

### Complete Teardown (Purging All Data)
Stops containers and permanently destroys the database volume and all task data:
```powershell
docker compose down -v
```

---

## 🐙 GitHub Setup & Push Guide

To push this project to GitHub repository:

```powershell
# 1. Initialize git
git init

# 2. Stage all project files
git add .

# 3. Create initial commit
git commit -m "first commit"

# 4. Set main branch
git branch -M main

# 5. Link GitHub remote
git remote add origin https://github.com/abhinav307/Multi-Container-TaskBoard-Application-using-Docker-Compose.git

# 6. Push to GitHub
git push -u origin main
```

---

## 📜 License & Acknowledgments

- Developed for **Program 14**: Multi-container applications using Docker Compose.
- Powered by [Docker Compose](https://docs.docker.com/compose/), [Flask](https://flask.palletsprojects.com/), and [PostgreSQL](https://www.postgresql.org/).
