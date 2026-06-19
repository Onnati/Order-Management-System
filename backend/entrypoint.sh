#!/bin/sh
set -e

echo "Waiting for database host 'db'..."
until python -c "
import socket
s = socket.socket()
s.settimeout(2)
s.connect(('db', 5432))
s.close()
" 2>/dev/null; do
  echo "Database not ready yet, retrying in 2s..."
  sleep 2
done

echo "Database is reachable. Running migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
