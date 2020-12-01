#!/bin/sh
set -e

cmd="$@"

postgres_ready () {
  python << END
from sys import exit as sys_exit
from psycopg2 import connect as connect_db, OperationalError


try:
    _ = connect_db(
        dbname="$POSTGRES_DB",
        user="$POSTGRES_USER",
        password="$POSTGRES_PASSWORD",
        host="postgres",
    )
except OperationalError:
    sys_exit(-1)
else:
    sys_exit(0)

END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."

exec $cmd
