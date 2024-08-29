#!/bin/bash
set -e

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Seed data
echo "Seed data"
python manage.py seed_data

# Start the Django server
exec "$@"