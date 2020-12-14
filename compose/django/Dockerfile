FROM python:3.9.0-slim-buster

ENV PYTHONUNBUFFERED=1

# Creates /app in container if it does not already exist
WORKDIR /app

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./pyproject.toml ./poetry.lock ./

RUN \
    DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends curl ca-certificates gnupg && \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
    "git=1:2.20.1-2+deb10u3" \
    "g++=4:8.3.0-1" \
    "libffi-dev=3.2.1-9" \
    "make=4.2.1-1.2" \
    "libopenblas-dev=0.3.5+ds-3" \
    "libpq-dev=11.9-0+deb10u1" && \
    DEBIAN_FRONTEND=noninteractive apt-get -y update && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends "postgresql-client-13" && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade --no-cache-dir pip && \
    python -m pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install

COPY . .

RUN \
    sed -i 's/\r//' ./compose/django/entrypoint.sh && chmod +x ./compose/django/entrypoint.sh && \
    sed -i 's/\r//' ./compose/django/start.sh      && chmod +x ./compose/django/start.sh

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "./compose/django/entrypoint.sh"]
