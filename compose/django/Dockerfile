FROM python:3.8.5-alpine3.12

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements.txt /requirements.txt

RUN apk add --no-cache "libffi-dev=3.3-r2" "g++=9.3.0-r2" "make=4.3-r0" "postgresql-dev=12.4-r0" "openblas-dev=0.3.9-r2" && \
    python -m pip install --upgrade pip && \
    python -m pip install -r /requirements.txt

COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh && chmod +x /entrypoint.sh

COPY . /app

COPY ./compose/django/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./compose/django/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh && chmod +x /start.sh

WORKDIR /app

RUN mkdir /data /data/static /data/media

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
