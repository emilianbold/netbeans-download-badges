#!/bin/bash
# Script to start the download counter service with gunicorn

# Configuration
WORKERS=2
BIND="127.0.0.1:5000"
LOG_LEVEL="info"
ACCESS_LOG="access.log"
ERROR_LOG="error.log"

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the application directory
cd "$DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "Error: gunicorn is not installed"
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

# Start gunicorn
echo "Starting download counter service..."
echo "Binding to: $BIND"
echo "Workers: $WORKERS"
echo "Access log: $ACCESS_LOG"
echo "Error log: $ERROR_LOG"

gunicorn \
    --workers "$WORKERS" \
    --bind "$BIND" \
    --log-level "$LOG_LEVEL" \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG" \
    --daemon \
    app:app

if [ $? -eq 0 ]; then
    echo "Service started successfully!"
    echo "PID file: gunicorn.pid (if configured)"
    echo ""
    echo "To stop the service, run: pkill gunicorn"
else
    echo "Failed to start service"
    exit 1
fi
