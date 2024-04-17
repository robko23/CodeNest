# Dump env for git hooks to work (and remove PWD and HOME vars)
env | sed '/^PWD/d' | sed '/^HOME/d'> /tmp/env
/usr/local/bin/python /app/manage.py migrate
if [[ -v DEVCONTAINER && $DEVCONTAINER == "true" ]]; then
    /usr/local/bin/python /app/manage.py runserver 0.0.0.0:8000
else
    /usr/local/bin/python -m gunicorn -b 0.0.0.0:8000 code-nest.wsgi
fi