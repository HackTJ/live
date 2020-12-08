#!/bin/sh
set -e

cmd="$@"  # provided in docker-compose.yml: services.django.command

postgres_ready () {
  python << END
from sys import exit as sys_exit
from psycopg2 import connect as connect_db, OperationalError


try:
    connect_db(
        dbname="$POSTGRES_DB",
        user="$POSTGRES_USER",
        password="$POSTGRES_PASSWORD",
        host="postgres",
    ).close()
except OperationalError:
    sys_exit(-1)
else:
    sys_exit(0)

END
}

until postgres_ready; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - continuing..."

chmod +x $cmd
exec $cmd
