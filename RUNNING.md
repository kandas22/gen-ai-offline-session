# Running GAF with Gunicorn

## Quick Start

### Option 1: Simple Script (Recommended)

```bash
./run_gunicorn.sh
```

This will:
- Kill any existing server on port 5001
- Start Gunicorn with 3 workers
- Log to `logs/access.log` and `logs/error.log`

### Option 2: Manual Gunicorn Command

```bash
gunicorn --workers 3 --bind 0.0.0.0:5001 --timeout 120 wsgi:app
```

### Option 3: Development Mode (Flask built-in server)

```bash
python app.py
```

## Configuration

### Workers
Edit `run_gunicorn.sh` and change `--workers 3` to your desired number.

### Port
Change `--bind 0.0.0.0:5001` to your desired port.

### Timeout
Change `--timeout 120` for longer/shorter timeouts.

## Stopping the Server

```bash
# Find and kill Gunicorn processes
lsof -t -i:5001 | xargs kill -9

# Or use the PID file
kill $(cat logs/gunicorn.pid)
```

## Viewing Logs

```bash
# Access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log
```

## Health Check

```bash
curl http://localhost:5001/
```

Expected response:
```json
{"service":"GAF Search Automation API","status":"healthy","version":"1.0.0"}
```

## Running in Background

```bash
nohup ./run_gunicorn.sh > /dev/null 2>&1 &
```

## Production Recommendations

1. **Use Nginx** as reverse proxy
2. **Enable HTTPS** with SSL certificates
3. **Set up monitoring** (e.g., Prometheus, Grafana)
4. **Configure firewall** to restrict access
5. **Use environment variables** for sensitive data
6. **Regular backups** of database and logs

## Troubleshooting

### Port already in use
```bash
lsof -t -i:5001 | xargs kill -9
```

### Permission denied
```bash
chmod +x run_gunicorn.sh
```

### Module not found
```bash
pip install -r requirements.txt
```

### Database connection failed
Check `DATABASE_URL` in `.env` file
