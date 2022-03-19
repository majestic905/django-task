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

    echo "Collecting static files..."
    python manage.py collectstatic --no-input --clear
    echo "Collecting static files finished"

    echo "Creating superuser..."
    if [ "$DJANGO_SUPERUSER_USERNAME" ]
    then
      python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
    fi
    echo "Created superuser"
fi

exec "$@"