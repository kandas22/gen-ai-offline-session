# Docker Deployment Guide

Complete guide for deploying GAF API using Docker.

## Quick Start

### 1. Build and Run

```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

### 2. Access the API

```
http://localhost:5001/
http://localhost:5001/api/docs
```

## Detailed Instructions

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Environment Setup

1. **Copy environment template**:
   ```bash
   cp .env.docker .env
   ```

2. **Update .env** with your configuration:
   ```env
   DATABASE_URL=your_supabase_url
   SERPAPI_KEY=your_api_key
   ```

### Building the Image

```bash
# Build with default settings
docker-compose build

# Build with no cache
docker-compose build --no-cache

# Build specific service
docker build -t gaf-api:latest .
```

### Building for Production (Linux/AMD64)

If you are building on a Mac (Apple Silicon) for deployment to a standard Linux server, you **MUST** specify the platform:

```bash
docker build --platform linux/amd64 -t gaf-api:latest .
```

### Running the Container

```bash
# Start in detached mode
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up gaf-api
```

### Managing Containers

```bash
# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove with volumes
docker-compose down -v

# Restart containers
docker-compose restart
```

### Viewing Logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f gaf-api

# Last 100 lines
docker-compose logs --tail=100 gaf-api
```

### Accessing the Container

```bash
# Execute bash shell
docker-compose exec gaf-api bash

# Run Python command
docker-compose exec gaf-api python -c "print('Hello')"

# Check Playwright installation
docker-compose exec gaf-api playwright --version
```

## Production Deployment

### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml gaf

# List services
docker service ls

# View service logs
docker service logs gaf_gaf-api
```

### Using Kubernetes

Create `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gaf-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gaf-api
  template:
    metadata:
      labels:
        app: gaf-api
    spec:
      containers:
      - name: gaf-api
        image: gaf-api:latest
        ports:
        - containerPort: 5001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: gaf-secrets
              key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: gaf-api-service
spec:
  selector:
    app: gaf-api
  ports:
  - port: 80
    targetPort: 5001
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `production` |
| `DEBUG` | Debug mode | `False` |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `HEADLESS_MODE` | Run browser headless | `True` |
| `BROWSER_TYPE` | Browser type | `chromium` |
| `PORT` | Server port | `5001` |

## Volume Mounts

The following directories are mounted for persistence:

- `./logs` → `/app/logs` - Application logs
- `./results` → `/app/results` - Test results
- `./screenshots` → `/app/screenshots` - Screenshots
- `./features/generated` → `/app/features/generated` - Generated tests

## Health Checks

The container includes a health check that:
- Runs every 30 seconds
- Times out after 10 seconds
- Retries 3 times before marking unhealthy
- Waits 40 seconds before starting

Check health status:
```bash
docker-compose ps
docker inspect gaf-api | grep -A 10 Health
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs gaf-api

# Check container status
docker-compose ps

# Rebuild without cache
docker-compose build --no-cache
```

### Playwright Issues

```bash
# Verify Playwright installation
docker-compose exec gaf-api playwright --version

# Reinstall browsers
docker-compose exec gaf-api playwright install chromium
```

### Database Connection Failed

```bash
# Test database connection
docker-compose exec gaf-api python -c "
from database.models import engine
print('Connected!' if engine else 'Failed')
"
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "5002:5001"  # Host:Container
```

## Performance Optimization

### Multi-stage Build

Create optimized Dockerfile:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
```

### Resource Limits

Add to docker-compose.yml:

```yaml
services:
  gaf-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Security Best Practices

1. **Don't commit .env files**
2. **Use secrets management**:
   ```yaml
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```
3. **Run as non-root user**:
   ```dockerfile
   RUN useradd -m -u 1000 gaf
   USER gaf
   ```
4. **Scan for vulnerabilities**:
   ```bash
   docker scan gaf-api:latest
   ```

## Monitoring

### Prometheus Metrics

Add to docker-compose.yml:

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Grafana Dashboard

```yaml
services:
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Backup and Recovery

### Backup Volumes

```bash
# Backup results
docker run --rm -v gaf_results:/data -v $(pwd):/backup \
  alpine tar czf /backup/results_backup.tar.gz /data

# Restore results
docker run --rm -v gaf_results:/data -v $(pwd):/backup \
  alpine tar xzf /backup/results_backup.tar.gz -C /
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build image
        run: docker build -t gaf-api:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
          docker push gaf-api:${{ github.sha }}
```

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify health: `docker-compose ps`
3. Test connectivity: `curl http://localhost:5001/`
