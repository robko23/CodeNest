# Create your views here.
import logging
import shutil
from datetime import datetime

import git.objects
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.text import slugify
from gitdb.exc import BadObject

from core.forms import NewIssueCommentForm
from core.forms import NewIssueForm
from core.forms import NewRepoForm
from core.forms import NewSSHKeyForm
from core.forms import NewWikiPageForm
from core.forms import RegisterForm
from core.models import Issue
from core.models import IssueComment
from core.models import Repository
from core.models import SSHKey
from core.models import WikiPage
from core.util.git import create_git_repo
from core.util.git import get_git_repo_absolute_path
from core.util.ssh import get_pubkey_fingerprint

log = logging.getLogger(__name__)
from git import Repo


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "register.html", {'form': form})


@login_required
def home(request):
    repos = Repository.objects.filter(Q(owner=request.user) | Q(collaborators__in=[request.user]))
    ssh_keys = SSHKey.objects.filter(owner=request.user)
    if request.method == "POST" and request.htmx:
        action = request.POST.get("action")
        object = request.POST.get("object")
        target = request.POST.get("target")
        if action == "delete" and object == "repository":
            repo = Repository.objects.get(owner=request.user, slug=target)
            repo.delete()
            shutil.rmtree(get_git_repo_absolute_path(f"{repo.owner.username}/{repo.slug}"))
            return render(request, "fragments/home/repo-list.html", {
                "repos": repos
            })
            pass
        elif action == "delete" and object == "ssh_key":
            ssh_key = SSHKey.objects.get(pk=target, owner=request.user)
            ssh_key.delete()
            return render(request, "fragments/home/ssh_keys.html", {
                "ssh_keys": ssh_keys
            })
        pass
    return render(request, "home.html", {
        'ssh_keys': ssh_keys,
        'repos':    repos,
    })


@login_required
def repo_detail(request, namespace: str, slug: str, ref: str = None, path: str = ""):
    try:
        db_repository = Repository.objects.filter(
            slug__exact=slug, owner__username__exact=namespace
        ).get(
            Q(owner=request.user) | Q(collaborators__in=[request.user])
        )
    except Repository.DoesNotExist:
        raise Http404(f"Repo {namespace}/{slug} does not exist or user does not have permissions")

    repo_path = get_git_repo_absolute_path(f"{namespace}/{slug}")
    repo = Repo(repo_path)

    branches = repo.branches
    current_ref_str = ref
    current_ref: git.types.AnyGitObject
    if ref:
        try:
            current_ref = repo.rev_parse(ref)
        except (BadObject, ValueError, IndexError):
            raise Http404(f"Ref {ref} does not exist in repo {namespace}/{slug}")
    else:
        current_ref = None
        for b in branches:
            b: git.Head = b
            if b.name in ('main', 'master', 'trunk'):
                current_ref = b.commit
                current_ref_str = b.name
        if not current_ref:
            return render(request, "repository/repo_empty.html", {
                "namespace": namespace,
                "slug":      slug
            })

    if path == '':
        current_object = current_ref.tree
    else:
        try:
            current_object = current_ref.tree.join(path)
        except KeyError:
            raise Http404(f"Path '{path}' does not exist in repo {namespace}/{slug} ref {ref}")

    tree: dict | None = None
    file: dict | None = None
    if isinstance(current_object, git.objects.Tree):
        files: list[git.objects.Blob] = list()
        dirs: list[git.objects.Tree] = list()
        for o in current_object.traverse(depth=1):
            if isinstance(o, git.objects.Tree):
                dirs.append(o)
            elif isinstance(o, git.objects.Blob):
                files.append(o)
        tree = {
            "dirs":  dirs,
            "files": files
        }
    elif isinstance(current_object, git.objects.Blob):
        if "/" in path:
            [_, filename] = path.rsplit("/", 1)
        else:
            filename = path
        file = {
            "contents": current_object.data_stream.read().decode('UTF-8'),
            "filename": filename
        }
        pass

    if path == '':
        back_url = None
    else:
        if "/" in path:
            [base, _file] = path.rsplit("/", 1)
        else:
            base = ""
        kwargs = {
            "namespace": namespace,
            "slug":      slug,
            "ref":       ref,
            "path":      base
        }
        back_url = reverse("repo_detail", kwargs=kwargs)

    return render(request, "repository/repo_detail.html", {
        "namespace":       db_repository.owner.username,
        "slug":            db_repository.slug,
        "branches":        branches,
        "path":            path,
        "current_ref":     current_ref,
        "tree":            tree,
        "file":            file,
        "current_ref_str": current_ref_str,
        "back_url":        back_url,
    })


def repo_commits(request, namespace, slug, ref):
    try:
        db_repository = Repository.objects.filter(
            slug__exact=slug, owner__username__exact=namespace
        ).get(
            Q(owner=request.user) | Q(collaborators__in=[request.user])
        )
    except Repository.DoesNotExist:
        raise Http404(f"Repo {namespace}/{slug} does not exist or user does not have permissions")

    repo_path = get_git_repo_absolute_path(f"{namespace}/{slug}")
    repo = Repo(repo_path)
    git_ref = repo.rev_parse(ref)

    commits: list[git.objects.Commit] = list()
    if isinstance(git_ref, git.objects.Commit):
        commits.append(git_ref)
    temp: git.types.Sequence[git.objects.Commit] = git_ref.parents

    while len(temp) > 0:
        c = temp[0]
        commits.append(c)

        temp = c.parents
        pass
    return render(request, "repository/repo_commits.html", {
        "namespace":     namespace,
        "slug":          slug,
        "commits":       commits,
        "commits_count": len(commits),
    })
    pass


@login_required
def new_ssh_key(request: WSGIRequest):
    if request.method == "POST":
        form = NewSSHKeyForm(request.POST)
        if form.is_valid():
            public_key = form.cleaned_data["public_key"]
            fingerprint = get_pubkey_fingerprint(public_key)
            if not fingerprint:
                return render(request, "new_ssh_key.html", {"form": form, "invalid_key": True})
            log.info(f"Adding new ssh key {fingerprint} to user {request.user.username}")
            ssh_key = SSHKey(name=form.cleaned_data["name"],
                             public_key=public_key,
                             fingerprint=fingerprint,
                             owner=request.user)
            ssh_key.save()
            return redirect(reverse("home"))

    form = NewSSHKeyForm()
    return render(request, "new_ssh_key.html", {"form": form})
    pass


def has_repo_permission(request: WSGIRequest, namespace: str, slug: str) -> bool:
    try:
        repository = Repository.objects.filter(
            slug__exact=slug, owner__username__exact=namespace
        ).get(
            Q(owner=request.user) | Q(collaborators__in=[request.user])
        )
    except Repository.DoesNotExist:
        raise Http404(f"Repo {namespace}/{slug} does not exist or user does not have permissions")

    return repository


@login_required
def new_repo(request: WSGIRequest):
    if request.method == "POST":
        form = NewRepoForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data["slug"]:
                form.cleaned_data["slug"] = slugify(form.cleaned_data["name"])
            already_exists = Repository.objects.filter(slug=form.cleaned_data["slug"],
                                                       owner=request.user).exists()
            if already_exists:
                return render(request, "new_repo.html", {"form": form, "slug_invalid": True})

            repo = Repository(name=form.cleaned_data["name"], slug=form.cleaned_data["slug"],
                              description=form.cleaned_data["description"],
                              owner=request.user)
            repo.save()

            create_git_repo(f"{request.user.username}/{repo.slug}")

            log.info(f"Creating new repo {form.cleaned_data['name']}")
            return redirect(reverse("home"))

    form = NewRepoForm()
    return render(request, "new_repo.html", {"form": form})
    pass


@login_required
def new_repo_issue(request: WSGIRequest, namespace: str, slug: str):
    try:
        repository = Repository.objects.filter(
            slug__exact=slug, owner__username__exact=namespace
        ).get(
            Q(owner=request.user) | Q(collaborators__in=[request.user])
        )
    except Repository.DoesNotExist:
        raise Http404(f"Repo {namespace}/{slug} does not exist or user does not have permissions")

    if request.method == "POST":
        form = NewIssueForm(request.POST)
        if form.is_valid():
            issue = Issue(title=form.cleaned_data["title"],
                          description=form.cleaned_data["description"],
                          repository=repository,
                          created_by=request.user)
            issue.save()

            return redirect(reverse("repo_issues", kwargs={"namespace": namespace, "slug": slug}))

    form = NewIssueForm()

    return render(request, "repository/issues/new_repo_issue.html", {
        "form":      form,
        "namespace": namespace,
        "slug":      slug
    })


@login_required
def repo_issues(request: WSGIRequest, namespace: str, slug: str):
    repository = has_repo_permission(request, namespace, slug)

    issues = Issue.objects.filter(repository=repository)

    return render(request, "repository/issues/repo_issues.html", {
        "namespace": namespace,
        "slug":      slug,
        "issues":    issues,
    })


@login_required
def repo_issue_detail(request: WSGIRequest, namespace: str, slug: str, issue_id: int):
    repository = has_repo_permission(request, namespace, slug)

    issue = Issue.objects.get(id=issue_id)
    issue_comments = IssueComment.objects.filter(issue=issue).order_by("created_at")

    comment_form = NewIssueCommentForm()

    return render(request, "repository/issues/repo_issue_detail.html", {
        "namespace": namespace,
        "slug":      slug,
        "issue":     issue,
        "form":      comment_form,
        "comments":  issue_comments
    })


@login_required
def repo_issue_comment(request: WSGIRequest, namespace: str, slug: str, issue_id: int):
    repository = has_repo_permission(request, namespace, slug)

    issue = Issue.objects.get(id=issue_id)

    if request.method == "POST":
        form = NewIssueCommentForm(request.POST)
        if form.is_valid():
            comment = IssueComment(text=form.cleaned_data["text"],
                                   created_by=request.user,
                                   issue=issue)
            comment.save()

            return redirect(reverse("repo_issue_detail",
                                    kwargs={"namespace": namespace, "slug": slug,
                                            "issue_id":  issue_id}))

    return render(request, "repository/issues/repo_issue_detail.html", {
        "namespace": namespace,
        "slug":      slug,
        "issue":     issue
    })


@login_required
def repo_issue_status(request: WSGIRequest, namespace: str, slug: str, issue_id: int, status: str):
    if request.method == "POST":
        repository = has_repo_permission(request, namespace, slug)

        issue = Issue.objects.get(id=issue_id)

        if status == "close":
            issue.closed_at = datetime.now()
        if status == "open":
            issue.closed_at = None

        issue.save()

        return redirect(reverse("repo_issue_detail", kwargs={"namespace": namespace, "slug": slug,
                                                             "issue_id":  issue_id}))


@login_required
def repo_wiki(request: WSGIRequest, namespace: str, slug: str):
    repository = has_repo_permission(request, namespace, slug)

    pages = WikiPage.objects.filter(repository=repository)

    return render(request, "repository/wiki/repo_wiki.html", {
        "namespace": namespace,
        "slug":      slug,
        "pages":     pages
    })


@login_required
def new_repo_wiki_page(request: WSGIRequest, namespace: str, slug: str):
    repository = has_repo_permission(request, namespace, slug)

    if request.method == "POST":
        form = NewWikiPageForm(request.POST)
        if form.is_valid():
            page = WikiPage(title=form.cleaned_data["title"],
                            content=form.cleaned_data["content"],
                            repository=repository,
                            created_by=request.user)
            page.save()

            return redirect(reverse("repo_wiki", kwargs={"namespace": namespace, "slug": slug}))

    form = NewWikiPageForm()

    return render(request, "repository/wiki/new_repo_wiki_page.html", {
        "form":      form,
        "namespace": namespace,
        "slug":      slug
    })
