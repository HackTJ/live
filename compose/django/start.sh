#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py createsuperuser --noinput  # from env vars

if [ "$DEBUG" == true ]
then
  python manage.py collectstatic --noinput --link

  python manage.py runserver 0.0.0.0:8000
else
  python manage.py collectstatic --noinput
  python manage.py compress  # django-compressor
  python -m whitenoise.compress static/assets/ ""  # whitenoise

  # uvicorn --host '0.0.0.0' --lifespan 'off' 'hacktj_live.asgi:application'
  ulimit -n 2048
  gunicorn --config ./compose/django/gunicorn.conf.py 'hacktj_live.asgi:application'
fi
