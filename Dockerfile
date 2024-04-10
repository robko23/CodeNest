FROM python:3

ENV DEBIAN_FRONTEND=noninteractive

RUN adduser git && \
    apt update && \
    apt install -y openssh-server supervisor && \
    mkdir /run/sshd

EXPOSE 2222

COPY docker/etc/supervisord.conf /etc/supervisord.conf
COPY docker/etc/ssh/sshd_config /etc/ssh/sshd_config

ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]
