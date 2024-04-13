#!/usr/bin/env python
import time

import django

django.setup()


def follow_file(file_name):
    fp = open(file_name, 'r')
    while True:
        new = fp.readline()
        if new:
            yield new.strip()
        else:
            time.sleep(0.2)


if __name__ == '__main__':
    import logging
    from django.conf import settings
    from django.core.cache import cache

    from core.models import SSHKey

    log = logging.getLogger(__name__)

    log.info(f"Starting sshd logwatch (file: {settings.SSHD_LOG_FILE_NAME})")

    log.debug("Truncating ssh log file")
    # trunc file
    with open(settings.SSHD_LOG_FILE_NAME, "w"):
        pass
    log.debug("File truncated, following it")

    # We need to parse this:
    # Accepted publickey for git from 172.17.0.1 port 51156 ssh2: RSA SHA256:DbE7JnXrfOL+MNjVk7QD8wUJ1z33MjoLkU53nZ+tD0
    for line in follow_file(settings.SSHD_LOG_FILE_NAME):
        if line.startswith(f"Accepted publickey for {settings.GIT_USERNAME} from"):
            modified = line.lstrip(f"Accepted publickey for {settings.GIT_USERNAME} from")
            [remote_ip, _port, remote_port, _ssh2, _rsa, fingerprint] = modified.split(" ")
            log.info(f"New connection from {remote_ip}:{remote_port} using {fingerprint}")

            try:
                used_ssh_key = SSHKey.objects.get(fingerprint__exact=fingerprint)
            except SSHKey.DoesNotExist:
                log.critical(f"SSH key {fingerprint} was used to connect, but it does not exist "
                             f"in database")
                continue

            cache.set(f"{remote_ip}:{remote_port}", used_ssh_key, timeout=15)
            pass

    pass
