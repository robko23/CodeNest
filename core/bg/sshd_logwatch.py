#!/usr/bin/env python
import time

import django
from django.conf import settings
from django.core.cache import cache

from core.models import SSHKey

django.setup()


def follow_file(file_name):
    fp = open(file_name, 'r')
    while True:
        new = fp.readline()
        if new:
            yield new.strip()
        else:
            time.sleep(0.2)


# trunc file
with open(settings.SSHD_LOG_FILE_NAME, "w"):
    pass

# We need to parse this:
# Accepted publickey for git from 172.17.0.1 port 51156 ssh2: RSA SHA256:DbE7JnXrfOL+MNjVk7QD8wUJ1z33MjoLkU53nZ+tD0
for line in follow_file(settings.SSHD_LOG_FILE_NAME):
    if line.startswith(f"Accepted publickey for {settings.GIT_USERNAME} from"):
        modified = line.lstrip(f"Accepted publickey for {settings.GIT_USERNAME} from")
        [remote_ip, _port, remote_port, _ssh2, _rsa, fingerprint] = modified.split(" ")
        used_ssh_key = SSHKey.objects.get(fingerprint__exact=fingerprint)

        cache.set(f"{remote_ip}:{remote_port}", used_ssh_key, timeout=15)
        pass
