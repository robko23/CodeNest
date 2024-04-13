/usr/local/bin/python /app/manage.py migrate
/usr/local/bin/python -m gunicorn -b 0.0.0.0:8000 code-nest.wsgi