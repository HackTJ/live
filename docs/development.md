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
export POSTGRES_USER=$(awk -F "\'" '/POSTGRES_USER/ { print $2; }' .env.local)
dropdb "$POSTGRES_USER"
export POSTGRES_PASSWORD=$(awk -F "\'" '/POSTGRES_PASSWORD/ { print $2; }' .env.local)
pg_ctl --pgdata=/usr/local/var/postgres initdb -U "$POSTGRES_USER" -P $POSTGRES_PASSWORD
pg_ctl --pgdata=/usr/local/var/postgres start
createdb "$POSTGRES_USER"
psql "$POSTGRES_USER" --file=./docs/setup.sql

export SECRET_KEY=$(awk -F "\'" '/SECRET_KEY/ { print $2; }' .env.local)
poetry run python manage.py migrate

unset POSTGRES_USER
unset POSTGRES_PASSWORD
unset SECRET_KEY
```

### Making Changes

-   If you update the [.env.local](./.env.local) file, make sure you surround all values with single quotes. If you rename the file, make sure to update this document with the correct name.
-   If you have direct commit/push access, be careful. Create PRs for big changes or any changes that might require testing, e.g., CI configuration updates.
-   ["Squash and merge"](https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/about-pull-request-merges#squash-and-merge-your-pull-request-commits) all PRs.
-   If you make any changes to the front-end/templates, make sure to run `pushd tailwind/ && NODE_ENV=production yarn build && popd`.
