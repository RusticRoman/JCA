# SKILL.md - Operations Runbook

## Deployment Skills

### Deploy a new version

1. Build the Docker image for AMD64 (required - Mac builds ARM by default):
   ```bash
   docker buildx build --platform linux/amd64 \
     -t us-central1-docker.pkg.dev/rich-gift-487522-m6/jca/jca-app:latest --push .
   ```

2. SSH into the VM and update:
   ```bash
   gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6 \
     --command="cd /opt/jca && sudo docker compose pull && sudo docker compose up -d --force-recreate"
   ```

3. Verify:
   ```bash
   curl http://35.188.107.106/health
   ```

### View logs

```bash
gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6 \
  --command="sudo docker compose -f /opt/jca/docker-compose.yml logs app --tail 100"
```

### Check container status

```bash
gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6 \
  --command="sudo docker compose -f /opt/jca/docker-compose.yml ps"
```

### Restart containers

```bash
gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6 \
  --command="cd /opt/jca && sudo docker compose restart"
```

### SSH into the VM

```bash
gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6
```

### Stop/Start the VM (save costs)

```bash
# Stop
gcloud compute instances stop jca-server --zone=us-central1-a --project=rich-gift-487522-m6

# Start
gcloud compute instances start jca-server --zone=us-central1-a --project=rich-gift-487522-m6
```

### Database access (via SSH)

```bash
gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6 \
  --command="sudo docker exec -it jca-postgres-1 psql -U jca -d jca"
```

### Create an admin user

1. Register a user at http://35.188.107.106/register
2. Update their role in the database:
   ```bash
   gcloud compute ssh jca-server --zone=us-central1-a --project=rich-gift-487522-m6 \
     --command="sudo docker exec jca-postgres-1 psql -U jca -d jca -c \"UPDATE users SET role='admin' WHERE email='YOUR_EMAIL';\""
   ```

## Local Development Skills

### Run the full stack locally

```bash
docker compose up
```
App at http://localhost:8000, API docs at http://localhost:8000/docs.

### Run tests

```bash
pytest -v
```

Tests use SQLite (no PostgreSQL needed). 74 tests: 3 unit + 71 integration.

### Run only unit tests

```bash
pytest tests/unit/ -v
```

### Run a specific test file

```bash
pytest tests/integration/test_admin.py -v
```

### Reset local database

```bash
docker compose down -v   # removes pgdata volume
docker compose up        # fresh start with seed data
```

### Run migrations manually

```bash
alembic upgrade head
```

## Seeded Test Accounts

| Role | Email | Password |
|------|-------|----------|
| Rabbi | `mentor@jca.org` | `mentor123` |
| Rabbi | `mentor2@jca.org` | `mentor456` |
| Student (x10) | `anna.p@example.com` etc. | `student123` |
| Admin | (none seeded) | Register + DB update |

## Infrastructure Details

| Resource | Value |
|----------|-------|
| GCP Project | `rich-gift-487522-m6` |
| GCE Instance | `jca-server` (e2-small, ~$12/mo) |
| Zone | `us-central1-a` (97% Carbon Free Energy) |
| External IP | `35.188.107.106` (ephemeral) |
| Container Registry | `us-central1-docker.pkg.dev/rich-gift-487522-m6/jca/jca-app` |
| Firewall Rule | `allow-http-jca` (TCP 80) |
| VM OS | Debian 12 + Docker CE |
| Compose Location | `/opt/jca/docker-compose.yml` (on VM) |
| Startup Script | `deploy/gce-startup.sh` (in repo) |
