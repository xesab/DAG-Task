#!/bin/sh

# Run Django migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Start the application using uvivorn
echo "Starting the application..."
exec "$@"