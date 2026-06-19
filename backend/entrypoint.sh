#!/bin/sh
set -e

echo "Waiting for database connection..."

python -c "
import os
import sys
import time

database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print('ERROR: DATABASE_URL environment variable is not set.')
    sys.exit(1)

if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

import psycopg2

max_attempts = 40
for attempt in range(1, max_attempts + 1):
    try:
        conn = psycopg2.connect(database_url)
        conn.close()
        print('Database connection successful.')
        break
    except Exception as exc:
        if attempt == max_attempts:
            print(f'ERROR: Could not connect to database after {max_attempts} attempts.')
            print(f'Last error: {exc}')
            sys.exit(1)
        print(f'Database not ready yet (attempt {attempt}/{max_attempts}), retrying in 3s...')
        time.sleep(3)
"

echo "Running migrations..."
alembic upgrade head

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
