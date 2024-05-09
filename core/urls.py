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

    path("repository/<str:namespace>/<str:slug>/issues/new", views.new_repo_issue, name="new_repo_issue"),
    path("repository/<str:namespace>/<str:slug>/issues", views.repo_issues, name="repo_issues"),
    path("repository/<str:namespace>/<str:slug>/issues/<str:issue_id>", views.repo_issue_detail, name="repo_issue_detail"),
    path("repository/<str:namespace>/<str:slug>/issues/<str:issue_id>/comment", views.repo_issue_comment, name="repo_issue_comment"),
    path("repository/<str:namespace>/<str:slug>/issues/<str:issue_id>/status/<str:status>", views.repo_issue_status, name="repo_issue_status"),

    path("repository/<str:namespace>/<str:slug>/wiki", views.repo_wiki, name="repo_wiki"),
    path("repository/<str:namespace>/<str:slug>/wiki/new", views.new_repo_wiki_page, name="new_repo_wiki_page"),

    path("", views.home, name="home"),
]
