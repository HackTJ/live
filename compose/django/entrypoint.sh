#!/bin/sh
set -e

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
