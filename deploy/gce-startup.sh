#!/bin/bash
set -e

# Install Docker via official method (includes compose plugin)
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable and start Docker
systemctl enable docker
systemctl start docker

# Authenticate Docker with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Create app directory
mkdir -p /opt/jca
cat > /opt/jca/docker-compose.yml <<'COMPOSE'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: jca
      POSTGRES_PASSWORD: jca
      POSTGRES_DB: jca
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jca"]
      interval: 2s
      timeout: 5s
      retries: 10
    restart: unless-stopped

  app:
    image: us-central1-docker.pkg.dev/rich-gift-487522-m6/jca/jca-app:latest
    ports:
      - "80:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://jca:jca@postgres:5432/jca
      FIREBASE_PROJECT_ID: ""
      FIREBASE_CREDENTIALS_PATH: ""
      CORS_ORIGINS: '["*"]'
      APP_BASE_URL: http://0.0.0.0:8000
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

volumes:
  pgdata:
COMPOSE

# Pull and start
cd /opt/jca
docker compose pull
docker compose up -d
