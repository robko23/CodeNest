#!/bin/sh
# Load dumped env from django-entrypoint.sh
export $(xargs </tmp/env)
python -m core.bg.ssh_client_wrapper
