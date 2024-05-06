from django.urls import path

import core.views as views

urlpatterns = [
    path("new_ssh_key", views.new_ssh_key, name="new_ssh_key"),
    path("new_repo", views.new_repo, name="new_repo"),
    # path(
    #     "repository/<str:namespace>/<str:slug>/refs/<str:ref>/<path:path>"
    #     , views.repo_listing,
    #     name="repo_listing"),
    path("repository/<str:namespace>/<str:slug>/", views.repo_detail, {"ref": None, "path": ""},
         name="repo_detail"),
    path("repository/<str:namespace>/<str:slug>/refs/<path:ref>/browse", views.repo_detail,
         {"path": ""},
         name="repo_detail"),
    path("repository/<str:namespace>/<str:slug>/refs/<path:ref>/browse/<path:path>",
         views.repo_detail,
         name="repo_detail"),
    path("repository/<str:namespace>/<str:slug>/refs/<path:ref>/commits",
         views.repo_commits, name="repo_commits"),
    path("", views.home, name="home"),
]
