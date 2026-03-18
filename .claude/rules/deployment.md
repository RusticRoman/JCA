---
paths:
  - "deploy/**"
  - "Dockerfile"
  - "docker-compose.yml"
  - ".github/**"
---

# Deployment Rules

- Images MUST be built for `linux/amd64` (Mac defaults to ARM): use `docker buildx build --platform linux/amd64`
- Container registry: `us-central1-docker.pkg.dev/rich-gift-487522-m6/jca/jca-app`
- GCE instance: `jca-server`, `e2-small`, zone `us-central1-a`, project `rich-gift-487522-m6`
- External IP: `35.188.107.106` (ephemeral)
- VM runs Docker Compose at `/opt/jca/docker-compose.yml` (postgres:16-alpine + app)
- Startup script: `deploy/gce-startup.sh` (installs Docker CE, pulls images, starts compose)
- Firewall rule: `allow-http-jca` (TCP 80)
- VM service account: `1070941009113-compute@developer.gserviceaccount.com` with `roles/artifactregistry.reader`
- Currently running in dev mode (no Firebase credentials), CORS `["*"]`
- `scripts/start.sh` is the container entrypoint: runs migrations → seeds → starts uvicorn on port 8000
