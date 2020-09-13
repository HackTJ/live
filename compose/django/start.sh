#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn hacktj_live:asgi -w 4 -k uvicorn.workers.UvicornWorker
