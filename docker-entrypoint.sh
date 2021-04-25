#!/bin/bash

set -e

echo "Collect static files"
python manage.py collectstatic --noinput

echo "Apply database migrations"
python manage.py migrate --noinput

rm -f /tmp/celerybeat.pid

exec "$@"