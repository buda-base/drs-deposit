# Docker Compose CLI Instructions

Use this compose file set in commands below:

```bash
-f docker-compose.yaml -f docker-compose-dev.yaml -f docker-compose-secrets.yaml
```

If your local file is actually named `docker-compose-escrets.yaml`, replace `docker-compose-secrets.yaml` in all commands.

## 1) Build with all three compose files

```bash
docker compose \
  -f docker-compose.yaml \
  -f docker-compose-dev.yaml \
  -f docker-compose-secrets.yaml \
  build
```

## 2) Rebuild airflow-worker only (using all three compose files)

```bash
docker compose \
  -f docker-compose.yaml \
  -f docker-compose-dev.yaml \
  -f docker-compose-secrets.yaml \
  build --no-cache airflow-worker
```

## 3) Compose down, then restart Docker (macOS)

```bash
docker compose \
  -f docker-compose.yaml \
  -f docker-compose-dev.yaml \
  -f docker-compose-secrets.yaml \
  down
```

Restart Docker Desktop manually, then verify:

```bash
docker info
```

Optional CLI restart (if installed):

```bash
osascript -e 'quit app "Docker"'
open -a Docker
```

## 4) Compose down, rebuild, and restart

```bash
docker compose \
  -f docker-compose.yaml \
  -f docker-compose-dev.yaml \
  -f docker-compose-secrets.yaml \
  down

docker compose \
  -f docker-compose.yaml \
  -f docker-compose-dev.yaml \
  -f docker-compose-secrets.yaml \
  build --no-cache

docker compose \
  -f docker-compose.yaml \
  -f docker-compose-dev.yaml \
  -f docker-compose-secrets.yaml \
  up -d
```
