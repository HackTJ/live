FROM python:3.9.0-alpine3.12

ENV PYTHONUNBUFFERED 1

# Creates /app in container if it does not already exist
WORKDIR /app

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY pyproject.toml poetry.lock ./

RUN apk add --no-cache \
    "g++=9.3.0-r2" \
    "libffi-dev=3.3-r2" \
    "make=4.3-r0" \
    "openblas-dev=0.3.9-r2" \
    "postgresql-dev=12.4-r0" && \
    python -m pip install --upgrade pip && \
    python -m pip install poetry --use-feature=2020-resolver && \
    poetry config virtualenvs.create false && \
    poetry install

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

COPY . .

COPY ./compose/django/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./compose/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh && chmod +x /start.sh

RUN mkdir /data /data/static /data/media

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
