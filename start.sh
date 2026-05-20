#!/bin/bash

# Exit immediately if any command fails (except checked commands)
set -e

# Print commands for easier debugging
set -x

echo "--------------------------------------------------"
echo "Starting Laptop Price Predictor Pro (Single Server)"
echo "--------------------------------------------------"

# Start redis-server if available, otherwise warn and fallback
if command -v redis-server >/dev/null 2>&1; then
  echo "Starting Redis cache database locally..."
  redis-server --port 6379 --daemonize yes
else
  echo "WARNING: redis-server command not found. Skipping Redis startup and falling back to in-memory cache."
fi

# Start FastAPI backend in the background on localhost, port 8000
echo "Starting FastAPI backend API locally..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 > fastapi.log 2>&1 &

# Wait for FastAPI backend to be fully online and ready to accept requests
echo "Waiting for FastAPI backend to spin up..."
for i in {1..20}; do
  if curl -s -f http://127.0.0.1:8000/ > /dev/null; then
    echo "FastAPI is up and running successfully!"
    break
  fi
  echo "Backend is starting up, waiting... ($i/20)"
  sleep 1
done

# Check if the backend failed to start and display logs if so
if ! curl -s -f http://127.0.0.1:8000/ > /dev/null; then
  echo "WARNING: FastAPI failed to start within 20 seconds. Printing logs:"
  if [ -f fastapi.log ]; then
    cat fastapi.log
  else
    echo "Log file not found."
  fi
fi

# Set default port for Streamlit if not provided
PORT=${PORT:-8501}
echo "Starting Streamlit frontend on public port: $PORT..."

# Run Streamlit in the foreground so the container stays active
exec streamlit run app.py --server.port "$PORT" --server.address 0.0.0.0 --server.headless true
