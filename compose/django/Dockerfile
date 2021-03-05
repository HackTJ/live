FROM python:3.9.2-slim-buster

ENV \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=0 \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  # poetry:
  POETRY_VERSION=1.1.5 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  PATH="$PATH:/root/.poetry/bin" \
  # tini:
  TINI_VERSION=v0.19.0

ARG DEBUG

# Creates /app in container if it does not already exist
WORKDIR /app

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./pyproject.toml ./poetry.lock ./

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN \
    # Install `postgresql-client` and `libpq-dev`:
    apt-get -y update \
    && apt-get install --no-install-recommends -y \
      "curl=7.64.0-4+deb10u1" \
      "ca-certificates=20200601~deb10u2" \
      "gnupg=2.2.12-1+deb10u1" \
    && curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main 13" > /etc/apt/sources.list.d/pgdg.list' \
    && apt-get -y update \
    && apt-get install --no-install-recommends -y \
      "postgresql-client-13=13.2-1.pgdg100+1" \
      "libpq-dev=13.2-1.pgdg100+1" \

    # Install dependencies of dependencies:
    && apt-get install --no-install-recommends -y \
      "git=1:2.20.1-2+deb10u3" \
      "g++=4:8.3.0-1" \
      "libffi-dev=3.2.1-9" \
      "make=4.2.1-1.2" \
      "libopenblas-dev=0.3.5+ds-3" \

    # Install dependencies of development dependencies:
    && if [[ "$DEBUG" = "true" ]]; then \
         apt-get install --no-install-recommends -y \
           "graphviz=2.40.1-6" \
         ; \
       fi \

    # Install Poetry and project dependencies:
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/$POETRY_VERSION/get-poetry.py | python - \
    && poetry config virtualenvs.create false \
    && poetry run python -m pip install --upgrade --no-cache-dir pip wheel \
    && if [[ "$DEBUG" = "true" ]]; then \
         poetry install; \
       else \
         poetry install --no-dev; \
       fi \

    # Install `tini`:
    && curl -L -o /tini "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini" \
    && chmod +x /tini \

    # Clean cache:
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
    && poetry cache clear --no-interaction pypi --all \
    && rm -rf ~/.cache/pypoetry/cache \
    && rm -rf ~/.cache/pypoetry/artifacts

COPY . .

RUN \
    sed -i 's/\r//' ./compose/django/entrypoint.sh && chmod +x ./compose/django/entrypoint.sh && \
    sed -i 's/\r//' ./compose/django/start.sh      && chmod +x ./compose/django/start.sh

EXPOSE 8000
ENTRYPOINT ["/tini", "--", "./compose/django/entrypoint.sh"]
