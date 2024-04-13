/usr/local/bin/python /app/manage.py migrate
if [[ -v DEVCONTAINER && $DEVCONTAINER == "true" ]]; then
    /usr/local/bin/python /app/manage.py runserver 0.0.0.0:8000
else
    /usr/local/bin/python -m gunicorn -b 0.0.0.0:8000 code-nest.wsgi
fi