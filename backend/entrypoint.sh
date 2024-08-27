#!/bin/bash
set -e

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate
echo "Apply hatchet permissions"
python manage.py hatchet_permissions

# Start the Django server
exec "$@"