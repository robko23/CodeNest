#!/usr/bin/env python
import time

# import django
#
# django.setup()

# TODO: move to settings
FILE_NAME = "aaa.txt"
GIT_USERNAME = "git"


def follow_file(file_name):
    fp = open(file_name, 'r')
    while True:
        new = fp.readline()
        if new:
            yield new.strip()
        else:
            time.sleep(0.2)


with open(FILE_NAME, "w"):
    pass

# We need to parse this:
# Accepted publickey for git from 172.17.0.1 port 51156 ssh2: RSA SHA256:DbE7JnXrfOL+MNjVk7QD8wUJ1z33MjoLkU53nZ+tD0
for line in follow_file(FILE_NAME):
    if line.startswith(f"Accepted publickey for {GIT_USERNAME} from"):
        modified = line.lstrip(f"Accepted publickey for {GIT_USERNAME} from")
        [remote_ip, _port, remote_port, _ssh2, _rsa, fingerprint] = modified.split(" ")
        # todo: insert userid by fingerprint info cache
        pass
    print(f"'{line}'")
