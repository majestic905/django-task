#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi


if [ -n "$MIGRATE_HERE" ]
then
    echo "Running migrations..."
    python manage.py migrate
    echo "Running migrations finished"
fi

exec "$@"