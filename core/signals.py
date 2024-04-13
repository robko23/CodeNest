import logging
import pathlib
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import SSHKey

log = logging.getLogger(__name__)


def _dump_ssh_keys():
    keys = SSHKey.objects.all()
    log.info(f'Writing {len(keys)} keys to authorized_keys file')
    pathlib.Path(settings.SSH_FOLDER).mkdir(parents=True, exist_ok=True)
    with open(settings.SSH_AUTHORIZED_KEYS_FILE, "w+") as f:
        for key in keys:
            f.write(key.public_key)
            f.write("\n")
            pass
        f.flush()
        pass
    pass


@receiver(post_save, sender=SSHKey)
def ssh_key_post_save(sender, **kwargs):
    _dump_ssh_keys()
    pass


@receiver(post_delete, sender=SSHKey)
def ssh_key_post_delete(sender, **kwargs):
    _dump_ssh_keys()
    pass


@receiver(pre_save, sender=User)
def user_pre_save(sender, **kwargs):
    instance = kwargs['instance']
    user = User.objects.get(pk=instance.pk)
    prev_username = user.username
    new_username = instance.username

    prev_path = settings.DATA_DIR / prev_username
    new_path = settings.DATA_DIR / new_username
    if os.path.isdir(prev_path):
        log.info(f"Renaming user repository namespace {prev_username} to {new_username}")
        os.rename(prev_path, new_path)
        pass
    pass
