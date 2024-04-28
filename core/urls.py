from django.urls import path

import core.views as views

urlpatterns = [
    path("new_ssh_key", views.new_ssh_key, name="new_ssh_key"),
    path("new_repo", views.new_repo, name="new_repo"),
    path(
        "repository/<str:namespace>/<str:slug>/refs/<str:commit_hash>/<path:path>"
        , views.repo_listing,
        name="repo_listing"),
    path("repository/<str:namespace>/<str:slug>/", views.repo_overview, name="repo_overview"),
    path("repository/<str:namespace>/<str:slug>/<path:branch_name>/", views.repo_overview,
         name="repo_overview"),
    # re_path(r"^repository/<str:namespace>/<str:slug>/(?P<branch_name>.*)$", views.repo_overview,
    #         name="repo_overview"),
    path("", views.home, name="home"),
]
