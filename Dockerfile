#syntax=docker/dockerfile:1.4
ARG PYTHON_IMAGE_NAME=python
ARG PYTHON_IMAGE_VERSION=3.12
FROM ${PYTHON_IMAGE_NAME}:${PYTHON_IMAGE_VERSION} as base

ENV DEBIAN_FRONTEND=noninteractive

RUN adduser git && \
    apt update && \
    apt install -y openssh-server supervisor && \
    mkdir /run/sshd

FROM ${PYTHON_IMAGE_NAME}:${PYTHON_IMAGE_VERSION} as python-packages

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY --link . .

RUN python manage.py collectstatic

FROM base as base-runner

WORKDIR /app

COPY --link docker/etc/supervisord.conf /etc/supervisord.conf
COPY --link docker/etc/ssh/sshd_config /etc/ssh/sshd_config
COPY --link docker/django-entrypoint.sh /django-entrypoint.sh
COPY --link docker/git-hooks /git-hooks

COPY --link --from=python-packages /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

ENV PYTHONPATH=/app
EXPOSE 2222
EXPOSE 8000

ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]

FROM base-runner as dev-runner

ENV DEVCONTAINER=true
ENV DJANGO_SETTINGS_MODULE=code-nest.settings.devcontainer

FROM base-runner as runner

COPY --link --from=python-packages /app /app

ENV DJANGO_SETTINGS_MODULE=code-nest.settings.container
