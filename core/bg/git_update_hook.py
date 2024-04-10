#!/usr/bin/env python
import os
import sys

if not os.getenv("GIT_DIR"):
    print("Do not run this script from command file", file=sys.stderr)
    print("It is intended to run this via git update hook", file=sys.stderr)
    exit(1)
    pass

refname = sys.argv[1]
oldrev = sys.argv[2]
newrev = sys.argv[3]

git_repo = os.getenv("PWD").lstrip(f"{os.getenv('HOME')}/")

# SSH_CLIENT=172.17.0.1 58146 22
ssh_info = os.getenv("SSH_CLIENT")
[remote_ip, port] = ssh_info.split(" ")

# todo: get from cache by remoteip and port, check if user has access to git_repo
