# Phase 6 Research: Infrastructure & Deployment

## Overview

This research covers Docker deployment for a FastAPI + React + PostgreSQL stack with healthchecks and automatic restarts.

---

## 1. Docker Compose Structure

### Recommended `docker-compose.yml` Structure

```yaml
services:
  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: wms
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - wms-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/wms
      SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - wms-network

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks:
      - wms-network

volumes:
  postgres_data:

networks:
  wms-network:
    driver: bridge
```

### Key Points

- **`depends_on` with `condition: service_healthy`** ensures proper startup order
- **Named volumes** for PostgreSQL data persistence
- **Bridge network** for inter-service communication
- **`restart: unless-stopped`** for automatic container restarts

---

## 2. Backend Dockerfile (FastAPI)

### Recommended `Dockerfile.backend`

```dockerfile
FROM python:3.12

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && fastapi run app/main.py --host 0.0.0.0 --port 8000"]
```

### Key Points

- **Python 3.12** base image (matches project requirements)
- **curl** installed for healthcheck
- **Requirements copied first** for Docker layer caching
- **Alembic migrations** run on container startup
- **`fastapi run`** (production mode, no auto-reload)

### Alternative: Multiple Workers

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && fastapi run app/main.py --host 0.0.0.0 --port 8000 --workers 4"]
```

---

## 3. Frontend Dockerfile (Vite + React)

### Recommended `Dockerfile.frontend` (Multi-stage)

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first for caching
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Production (nginx)
FROM nginx:alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf (Required)

```nginx
server {
    listen 80;
    server_name localhost;

    # Serve static files
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Healthcheck endpoint
    location /health {
        access_log off;
        return 200 "ok";
        add_header Content-Type text/plain;
    }
}
```

### Key Points

- **Multi-stage build** keeps final image small
- **nginx:alpine** for lightweight production serving
- **`try_files`** handles React Router (SPA) routing
- **API proxy** to backend via Docker network
- **/health endpoint** for container healthcheck

---

## 4. Healthcheck Implementations

### PostgreSQL Healthcheck

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

- Uses built-in `pg_isready` command
- `start_period` allows initialization time

### Backend Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

- Requires `/health` endpoint (already exists in `app/main.py:65`)
- `start_period: 40s` accounts for migrations

### Frontend Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 5s
  retries: 3
```

- nginx serves `/health` directly (fast response)

---

## 5. Environment Variable Strategy

### Backend Environment Variables

```yaml
backend:
  environment:
    DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/wms
    SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
    DEBUG: "false"
```

**Key Points:**
- Use `.env` file for secrets (not committed to git)
- Default values with `${VAR:-default}` syntax
- Hostname is **service name** (`postgres`), not `localhost`

### Frontend Environment Variables

**Build-time variables** (in Vite):
```dockerfile
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
```

**Runtime via nginx proxy** (recommended):
- Frontend calls `/api/*` 
- nginx proxies to `http://backend:8000`
- No hardcoded API URL needed

### `.env` Example (create, don't commit)

```env
SECRET_KEY=your-super-secret-key-here
DB_PASSWORD=secure-password
```

### `.dockerignore`

```
**/.env
**/.env.*
**/node_modules
**/__pycache__
**/*.pyc
**/.git
**/.gitignore
```

---

## 6. Volume Strategy

### PostgreSQL Volume

```yaml
volumes:
  postgres_data:
```

- **Named volume** managed by Docker
- Data persists across container restarts/recreations
- Location: `/var/lib/docker/volumes/wh_postgres_data/_data`

### Inspect Volume

```bash
docker volume ls
docker volume inspect wh_postgres_data
```

### Backup Strategy (Optional)

```bash
docker compose exec postgres pg_dump -U postgres wms > backup.sql
```

---

## 7. Network Configuration

### Default Bridge Network

```yaml
networks:
  wms-network:
    driver: bridge
```

**Service Discovery:**
- Services reach each other by **service name**
- `postgres:5432` for database
- `backend:8000` for API

### Port Exposure Strategy

```yaml
postgres:
  # No ports exposed - only internal access

backend:
  # No ports exposed - only via nginx proxy

frontend:
  ports:
    - "80:80"  # Single entry point
```

**Security:** Only frontend (nginx) is exposed externally.

---

## 8. Restart Policies

### Options

| Policy | Behavior |
|--------|----------|
| `no` | Never restart (default) |
| `always` | Always restart |
| `unless-stopped` | Restart unless manually stopped |
| `on-failure` | Restart only on failure |

### Recommended: `unless-stopped`

```yaml
restart: unless-stopped
```

- Restarts on crash, system reboot
- Allows manual stop via `docker compose stop`
- Survives Docker daemon restart

---

## 9. Common Pitfalls to Avoid

### 1. **Database Not Ready**

**Problem:** Backend starts before PostgreSQL is ready.

**Solution:** Use `depends_on` with `condition: service_healthy`:
```yaml
depends_on:
  postgres:
    condition: service_healthy
```

### 2. **localhost vs Service Name**

**Problem:** Using `localhost` in Docker network.

**Solution:** Use service names:
- ❌ `DATABASE_URL: postgresql://postgres@localhost:5432/wms`
- ✅ `DATABASE_URL: postgresql://postgres@postgres:5432/wms`

### 3. **React Router 404**

**Problem:** Refreshing SPA pages returns 404.

**Solution:** nginx `try_files` directive:
```nginx
try_files $uri $uri/ /index.html;
```

### 4. **Missing curl in Containers**

**Problem:** Healthcheck fails because curl isn't installed.

**Solution:** Install curl in Dockerfile:
```dockerfile
RUN apt-get install -y curl  # Debian
RUN apk add --no-cache curl  # Alpine
```

### 5. **Secrets in Image**

**Problem:** Hardcoded secrets in Dockerfile.

**Solution:** Pass at runtime:
```yaml
environment:
  SECRET_KEY: ${SECRET_KEY}
```

### 6. **Alembic URL Mismatch**

**Problem:** `alembic.ini` has hardcoded URL, container has different.

**Solution:** Override in `env.py` or use environment variable:
```python
# In alembic/env.py
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### 7. **Large Images**

**Problem:** Copying unnecessary files.

**Solution:** Use `.dockerignore` and multi-stage builds.

---

## 10. Files to Create

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Multi-service orchestration |
| `Dockerfile.backend` | Backend container image |
| `Dockerfile.frontend` | Frontend container image |
| `nginx.conf` | nginx reverse proxy config |
| `.dockerignore` | Exclude files from build context |
| `.env.example` | Template for environment variables |

---

## 11. Quick Reference Commands

```bash
# Build and start all services
docker compose up -d --build

# View logs
docker compose logs -f

# Check health status
docker compose ps

# Stop all services
docker compose down

# Remove volumes (reset database)
docker compose down -v

# Rebuild single service
docker compose up -d --build backend
```

---

## 12. Implementation Checklist

- [ ] Create `docker-compose.yml`
- [ ] Create `Dockerfile.backend`
- [ ] Create `Dockerfile.frontend`
- [ ] Create `nginx.conf`
- [ ] Create `.dockerignore`
- [ ] Create `.env.example`
- [ ] Update `alembic/env.py` to use env var for DB URL
- [ ] Test `docker compose up --build`
- [ ] Verify healthchecks: `docker compose ps`
- [ ] Test container restart: `docker compose restart backend`
- [ ] Test full cycle: `docker compose down && docker compose up -d`
