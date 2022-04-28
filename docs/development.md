# HackTJ Live

## Development

```sh
git clone git@github.com:HackTJ/live.git  # or git clone https://github.com/HackTJ/live.git
cd live/
```

### Docker Compose

This is slower to build but much easier to use/configure. We recommend developing in Docker Compose so that environments are consistent.

```sh
./start_live dev
```

When you need to wipe all data:

```sh
docker compose down --remove-orphans --volumes  # don't forget the following command!
rm -rf data/
```

### Without Docker Compose

#### Django Setup

```sh
poetry install
poetry run pre-commit install
```

#### Database Setup

```sh
export POSTGRES_USER="$(cat ./compose/secrets/development/postgres_user.txt)"
dropdb "$POSTGRES_USER"
export POSTGRES_PASSWORD="$(cat ./compose/secrets/development/postgres_password.txt)"
pg_ctl --pgdata=/usr/local/var/postgres initdb -U "$POSTGRES_USER" -P $POSTGRES_PASSWORD
pg_ctl --pgdata=/usr/local/var/postgres start
createdb "$POSTGRES_USER"
psql "$POSTGRES_USER" --file=./docs/setup.sql

export SECRET_KEY="$(cat ./compose/secrets/development/secret_key.txt)"
poetry run python manage.py migrate

unset POSTGRES_USER
unset POSTGRES_PASSWORD
unset SECRET_KEY
```

### Making Changes

-   If you have direct commit/push access, be careful. Create PRs for big changes or any changes that might require testing, e.g., CI configuration updates.
-   ["Squash and merge"](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-request-merges#squash-and-merge-your-pull-request-commits) all PRs.
-   If you make any changes to the front-end (the Django templates), make sure to run `pushd tailwind/ && NODE_ENV=production yarn run build && popd`.
