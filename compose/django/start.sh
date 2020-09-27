#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py compress

# uvicorn --host '0.0.0.0' --lifespan 'off' 'hacktj_live.asgi:application'
gunicorn --config ./compose/django/gunicorn.conf.py 'hacktj_live.asgi:application'
