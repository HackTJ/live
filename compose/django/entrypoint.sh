#!/bin/sh
set -e

# these are all paths to files under /run/secrets
export \
  SECRET_KEY="$(cat $SECRET_KEY)" \
  DJANGO_SUPERUSER_USERNAME="$(cat $DJANGO_SUPERUSER_USERNAME)" \
  DJANGO_SUPERUSER_PASSWORD="$(cat $DJANGO_SUPERUSER_PASSWORD)" \
  DJANGO_SUPERUSER_EMAIL="$(cat $DJANGO_SUPERUSER_EMAIL)" \
  POSTGRES_USER="$(cat $POSTGRES_USER)" \
  POSTGRES_PASSWORD="$(cat $POSTGRES_PASSWORD)" \
  POSTGRES_DB="$(cat $POSTGRES_DB)" \
  SENDGRID_API_KEY="$(cat $SENDGRID_API_KEY)"

urlencode () {
    python3 - "$@" << END
from urllib.parse import quote_plus
from sys import argv


print(quote_plus(" ".join(argv[1:])))

END
}

ENCODED_DATABASE_URL=$(urlencode "$DATABASE_URL")

until pg_isready --dbname="$ENCODED_DATABASE_URL" --host="postgres" --username="$POSTGRES_USER"; do
  sleep 1
done

# provided in docker-compose.yml: services.django.command
chmod +x "$@"
exec "$@"
