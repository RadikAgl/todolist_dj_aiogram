#!/bin/sh
set -e
# Ждём доступности БД
until python manage.py migrate --check 2>/dev/null; do
  echo "Waiting for migrations to be applied..."
  sleep 2
done
exec "$@"