#!/bin/bash

# Simple Gunicorn startup script
# No virtual environment required

echo "Starting GAF API with Gunicorn..."

# Create logs directory
mkdir -p logs

# Kill any existing Gunicorn processes on port 5001
lsof -t -i:5001 | xargs kill -9 2>/dev/null || true

# Remove stale PID file
rm -f logs/gunicorn.pid

# Start Gunicorn with 3 workers
gunicorn \
    --workers 3 \
    --bind 0.0.0.0:5001 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --pid logs/gunicorn.pid \
    wsgi:app

echo "Server stopped"
