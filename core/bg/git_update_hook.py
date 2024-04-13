#!/usr/bin/env python
import os
import sys

import django

django.setup()

if __name__ == '__main__':
    from core.models import Profile
    from core.models import Repository
    from core.models import SSHKey
    from django.core.cache import cache

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

    used_ssh_key: SSHKey | None = cache.get(f"{remote_ip}:{port}")
    if not used_ssh_key:
        print("Permission denied (no connection log)", file=sys.stderr)
        exit(1)

    [user, reponame] = git_repo.split("/")
    if user is None or reponame is None:
        print("Permission denied (invalid path)", file=sys.stderr)
        exit(1)

    try:
        profile = Profile.objects.get(user=used_ssh_key.owner, slug__exact=user)
        repo = Repository.objects.get(owner=used_ssh_key.owner, slug__exact=reponame)
    except (Profile.DoesNotExist, Repository.DoesNotExist):
        print("Permission denied", file=sys.stderr)
        exit(1)
