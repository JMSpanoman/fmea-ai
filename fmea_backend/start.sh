#!/bin/bash

# Render stability defaults (avoid OOM with too many workers on small instances)
export PORT="${PORT:-8000}"
export WEB_CONCURRENCY="${WEB_CONCURRENCY:-1}"
export GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"

# Initialize database (only if missing)
echo "Initializing database (if needed)..."
if [ ! -f "/app/db/fmea.db" ]; then
  python /app/init_db.py
fi

# Start the application
echo "Starting application..."
exec gunicorn main:app \
  --workers "$WEB_CONCURRENCY" \
  --timeout "$GUNICORN_TIMEOUT" \
  -k uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:$PORT"
