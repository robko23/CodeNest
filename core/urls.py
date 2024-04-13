from django.urls import path

import core.views as views

urlpatterns = [
    path("new_ssh_key", views.new_ssh_key, name="new_ssh_key"),
    path("new_repo", views.new_repo, name="new_repo"),
    path("", views.home, name="home"),
]
