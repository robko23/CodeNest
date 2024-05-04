from django.contrib.auth.models import User
from django.db import models


class Repository(models.Model):
    owner = models.ForeignKey(User, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=500, null=True, blank=True)
    slug = models.CharField(max_length=30, null=False, blank=False)
    collaborators = models.ManyToManyField(User, related_name="collaborators", blank=True)

    def __str__(self):
        return f"{self.name} ( {self.owner.username}/{self.slug} )"


class SSHKey(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False)
    public_key = models.TextField(null=False, blank=False, unique=True)
    fingerprint = models.CharField(max_length=60, blank=False, null=False, unique=True)

    def __str__(self):
        return self.fingerprint
    
class Issue(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=512, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
class IssueComment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    text = models.CharField(max_length=512, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
    
class WikiPage(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False, blank=False)
    content = models.CharField(max_length=512, null=False, blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Snippet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
class SnippetFile(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False, blank=False)
    content = models.CharField(max_length=512, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# this needs to be at the bottom of the file, because it would create circular import error.
# we need to import this to register the signals
# noinspection all
import core.signals
