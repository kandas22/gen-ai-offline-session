"""
Gunicorn configuration file for GAF API
Production-ready settings for Flask application
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes
workers = 3  # Fixed worker count
worker_class = "sync"
worker_connections = 1000
timeout = 120  # Increased for long-running Playwright tests
keepalive = 5

# Restart workers after this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "gaf_api"

# Server mechanics
daemon = False
pidfile = "logs/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("Starting Gunicorn server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("Reloading Gunicorn server...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"Gunicorn server is ready. Listening on {bind}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("Shutting down Gunicorn server...")

# Development settings (override in production)
reload = os.getenv("FLASK_ENV") == "development"
reload_extra_files = []

# Preload application for better performance
preload_app = True
