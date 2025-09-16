#!/bin/bash

# Initialize database
echo "Initializing database..."
python /app/init_db.py

# Start the application
echo "Starting application..."
exec gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
