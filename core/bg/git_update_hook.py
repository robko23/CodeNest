#!/usr/bin/env python
import os
import sys

import django

django.setup()

if __name__ == '__main__':
    if not os.getenv("GIT_DIR"):
        print("Do not run this script from command file", file=sys.stderr)
        print("It is intended to run this via git update hook", file=sys.stderr)
        exit(1)
        pass

    refname = sys.argv[1]
    oldrev = sys.argv[2]
    newrev = sys.argv[3]
