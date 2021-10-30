FROM python:3.9.7-slim-bullseye

ENV \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=0 \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  # poetry:
  POETRY_VERSION=1.1.11 \
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
      "curl=7.74.0-1.3+b1" \
      "ca-certificates=20210119" \
      "gnupg=2.2.27-2" \
    && curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt bullseye-pgdg 13" > /etc/apt/sources.list.d/pgdg.list' \
    && apt-get -y update \
    && apt-get install --no-install-recommends -y \
      "postgresql-client-13=13.4-0+deb11u1" \
      "libpq-dev=13.4-4.pgdg110+1" \

    # Install dependencies of dependencies:
    && apt-get install --no-install-recommends -y \
      "git=1:2.30.2-1" \
      "g++=4:10.2.1-1" \
      "libffi-dev=3.3-6" \
      "make=4.3-4.1" \
      "libopenblas-dev=0.3.13+ds-3" \

    # Install dependencies of development dependencies:
    && if [[ "$DEBUG" = "true" ]]; then \
         apt-get install --no-install-recommends -y \
           "graphviz=2.42.2-5" \
         ; \
       fi \

    # Install Poetry and project dependencies:
    && curl -sSL "https://raw.githubusercontent.com/python-poetry/poetry/$POETRY_VERSION/get-poetry.py" | python - \
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
