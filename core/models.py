from django.contrib.auth.models import User
from django.db import models


class Repository(models.Model):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    slug = models.CharField(max_length=30, null=False, blank=False)

    def __str__(self):
        return f"{self.name} ( {self.owner.username}/{self.slug} )"


class SSHKey(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False)
    public_key = models.TextField(null=False, blank=False, unique=True)
    fingerprint = models.CharField(max_length=60, blank=False, null=False, unique=True)

    def __str__(self):
        return self.fingerprint


# this needs to be at the bottom of the file, because it would create circular import error.
# we need to import this to register the signals
# noinspection PyUnresolvedReferences
import core.signals
