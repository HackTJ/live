#!/bin/sh
set -e

cmd="$@"

django_ready () {
  nc -z "django" "8000" > /dev/null 2>&1
}

until django_ready; do
  >&2 echo "Django is unavailable - sleeping"
  sleep 1
done

>&2 echo "Django is up - continuing..."

exec nginx -g 'daemon off;'
