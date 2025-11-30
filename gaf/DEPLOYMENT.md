# Production Deployment Guide

This guide covers deploying the GAF API to production using Gunicorn.

## Prerequisites

- Python 3.8+
- Virtual environment
- PostgreSQL database (Supabase)
- Nginx (recommended for reverse proxy)

## Quick Start

### 1. Install Gunicorn

```bash
pip install gunicorn
```

### 2. Start the Server

```bash
./start.sh
```

Or manually:

```bash
gunicorn --config gunicorn_config.py wsgi:app
```

## Production Configuration

### Gunicorn Settings

The `gunicorn_config.py` file includes optimized production settings:

- **Workers**: `CPU cores * 2 + 1` (auto-calculated)
- **Timeout**: 120 seconds (for long-running tests)
- **Max Requests**: 1000 (prevents memory leaks)
- **Logging**: Access and error logs in `logs/` directory

### Environment Variables

Ensure `.env` file contains:

```env
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:password@host:5432/database
```

## Systemd Service (Linux)

### 1. Copy Service File

```bash
sudo cp gaf.service /etc/systemd/system/
```

### 2. Update Paths

Edit `/etc/systemd/system/gaf.service`:

```ini
WorkingDirectory=/path/to/your/gaf
Environment="PATH=/path/to/your/gaf/venv/bin"
ExecStart=/path/to/your/gaf/venv/bin/gunicorn --config gunicorn_config.py wsgi:app
```

### 3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable gaf
sudo systemctl start gaf
```

### 4. Check Status

```bash
sudo systemctl status gaf
```

### 5. View Logs

```bash
sudo journalctl -u gaf -f
```

## Nginx Reverse Proxy (Recommended)

### Configuration

Create `/etc/nginx/sites-available/gaf`:

```nginx
upstream gaf_api {
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logging
    access_log /var/log/nginx/gaf_access.log;
    error_log /var/log/nginx/gaf_error.log;

    # Proxy settings
    location / {
        proxy_pass http://gaf_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running tests
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://gaf_api/;
        access_log off;
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/gaf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5001

# Run with Gunicorn
CMD ["gunicorn", "--config", "gunicorn_config.py", "wsgi:app"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  gaf-api:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - ./logs:/app/logs
      - ./results:/app/results
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Build and Run

```bash
docker-compose up -d
```

## Monitoring

### Health Check

```bash
curl http://localhost:5001/
```

### View Logs

```bash
tail -f logs/access.log
tail -f logs/error.log
```

### Monitor Workers

```bash
ps aux | grep gunicorn
```

## Performance Tuning

### Worker Count

Adjust in `gunicorn_config.py`:

```python
workers = 4  # Fixed number
# OR
workers = multiprocessing.cpu_count() * 2 + 1  # Auto-scale
```

### Timeout

For longer tests, increase timeout:

```python
timeout = 300  # 5 minutes
```

### Memory Management

Restart workers periodically:

```python
max_requests = 1000
max_requests_jitter = 50
```

## Security Best Practices

1. **Use HTTPS** - Always use SSL/TLS in production
2. **Environment Variables** - Never commit `.env` file
3. **Firewall** - Restrict access to port 5001
4. **Rate Limiting** - Use Nginx rate limiting
5. **Authentication** - Implement API authentication
6. **CORS** - Configure allowed origins

## Troubleshooting

### Port Already in Use

```bash
lsof -t -i:5001 | xargs kill -9
```

### Permission Denied

```bash
sudo chown -R $USER:$USER /path/to/gaf
```

### Database Connection Failed

Check `DATABASE_URL` and network connectivity:

```bash
psql $DATABASE_URL -c "SELECT 1"
```

### High Memory Usage

Reduce worker count or enable max_requests:

```python
workers = 2
max_requests = 500
```

## Scaling

### Horizontal Scaling

Deploy multiple instances behind a load balancer:

```nginx
upstream gaf_cluster {
    server 10.0.0.1:5001;
    server 10.0.0.2:5001;
    server 10.0.0.3:5001;
}
```

### Database Connection Pooling

Use pgbouncer for PostgreSQL connection pooling.

## Backup and Recovery

### Database Backups

```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Application Backups

```bash
tar -czf gaf_backup_$(date +%Y%m%d).tar.gz \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='__pycache__' \
    .
```

## Support

For issues, check:
- Application logs: `logs/error.log`
- System logs: `sudo journalctl -u gaf`
- Nginx logs: `/var/log/nginx/gaf_error.log`
