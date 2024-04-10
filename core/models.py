from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pass


class Repository(models.Model):
    owner = models.OneToOneField(User, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    pass


class SSHKey(models.Model):
    owner = models.ManyToManyField(User)
    name = models.CharField(max_length=50, null=False, blank=False)
    public_key = models.TextField(null=False, blank=False)
    fingerprint = models.CharField(max_length=60, blank=False, null=False)
