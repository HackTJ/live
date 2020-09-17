module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:8000/'],
      startServerCommand: 'DEBUG=FALSE SECRET_KEY=bad_secret gunicorn --config ./compose/django/gunicorn.conf.py --bind localhost:8000 hacktj_live.asgi:application',
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
