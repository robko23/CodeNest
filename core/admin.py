from django.contrib import admin

import core.models as models

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Repository)
class RepositoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SSHKey)
class SSHKeyAdmin(admin.ModelAdmin):
    pass
