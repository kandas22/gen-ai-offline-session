#!/bin/bash

# GAF API Startup Script
# Production deployment with Gunicorn

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting GAF API...${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}Gunicorn not found. Installing...${NC}"
    pip install gunicorn
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Please create .env file with required configuration"
fi

# Start Gunicorn
echo -e "${GREEN}Starting Gunicorn server...${NC}"
gunicorn --config gunicorn_config.py wsgi:app

# If we get here, the server has stopped
echo -e "${YELLOW}Server stopped${NC}"
