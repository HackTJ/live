#!/bin/bash

poetry run python manage.py makemigrations --noinput
poetry run python manage.py migrate --noinput
poetry run python manage.py createsuperuser --noinput  # from env vars

if [ "$DEBUG" == true ]
then
  poetry run python manage.py loaddata --exclude contenttypes 'data-75'

  poetry run python manage.py collectstatic --noinput --link

  poetry run python manage.py runserver 0.0.0.0:8000
else
  poetry run python manage.py collectstatic --noinput
  poetry run python manage.py compress  # django-compressor
  poetry run python -m whitenoise.compress static/assets/ ""  # whitenoise

  ulimit -n 2048
  poetry run gunicorn --config ./compose/django/gunicorn.conf.py 'hacktj_live.asgi:application'
fi
