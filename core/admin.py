from django.contrib import admin

import core.models as models


@admin.register(models.Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "slug")
    pass


@admin.register(models.SSHKey)
class SSHKeyAdmin(admin.ModelAdmin):
    list_display = ("owner", "name", "fingerprint")
    pass


@admin.register(models.Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("repository", "title", "created_by", "created_at")
    pass


@admin.register(models.IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    list_display = ("issue", "text", "created_by", "created_at")
    pass


@admin.register(models.WikiPage)
class WikiPageAdmin(admin.ModelAdmin):
    list_display = ("repository", "title", "created_at", "created_by")
    pass
