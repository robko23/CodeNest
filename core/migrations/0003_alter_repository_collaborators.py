# Generated by Django 5.0.4 on 2024-04-28 11:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_repository_collaborators'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='repository',
            name='collaborators',
            field=models.ManyToManyField(blank=True, related_name='collaborators', to=settings.AUTH_USER_MODEL),
        ),
    ]
