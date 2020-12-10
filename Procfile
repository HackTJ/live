web: python manage.py makemigrations --noinput; python manage.py migrate --noinput; python manage.py createsuperuser --noinput; python manage.py collectstatic --noinput; python manage.py compress; bin/start-pgbouncer gunicorn --config ./compose/django/gunicorn.conf.py 'hacktj_live.asgi:application'
worker: python manage.py runworker
