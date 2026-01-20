#!/bin/bash

# Render stability defaults (avoid OOM with too many workers on small instances)
export PORT="${PORT:-8000}"
export WEB_CONCURRENCY="${WEB_CONCURRENCY:-1}"
export GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"

# Database initialization is handled by SQLAlchemy on app startup (see main.py lifespan).
# We intentionally do not run init_db.py here because it can create a schema that does not
# match the SQLAlchemy models (causing auth/runtime failures).

# Start the application
echo "Starting application..."
exec gunicorn main:app \
  --workers "$WEB_CONCURRENCY" \
  --timeout "$GUNICORN_TIMEOUT" \
  -k uvicorn.workers.UvicornWorker \
  --bind "0.0.0.0:$PORT"
