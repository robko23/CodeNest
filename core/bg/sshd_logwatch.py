import time

# import django
#
# django.setup()

FILE_NAME = "aaa.txt"


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

# Accepted publickey for git from 172.17.0.1 port 51156 ssh2: RSA SHA256:DbE7JnXrfOL+MNjVk7QD8wUJ1z33MjoLkU53nZ+tD0
for line in follow_file(FILE_NAME):
    print(f"'{line}'")
