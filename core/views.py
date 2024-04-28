# Create your views here.
import logging
import shutil

import git.objects
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from core.forms import NewRepoForm
from core.forms import NewSSHKeyForm
from core.models import Repository
from core.models import SSHKey
from core.util.git import create_git_repo
from core.util.git import get_git_repo_absolute_path
from core.util.ssh import get_pubkey_fingerprint

log = logging.getLogger(__name__)
from git import Repo


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
def repo_detail(request, namespace: str, slug: str, branch_name: str = None):
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

    # select default branch
    branch: git.Head | None = None
    if branch_name:
        for b in branches:
            if b.name == branch_name:
                branch = b
        if not branch:
            raise Http404(f"Branch {branch_name} does not exist in repo {namespace}/{slug}")
    else:
        for b in branches:
            if b.name in ('main', 'master', 'trunk'):
                branch = b
        if not branch:
            return render(request, "repo_empty.html", {
                "namespace": namespace,
                "slug":      slug
            })

    files: list[git.objects.Blob] = list()
    dirs: list[git.objects.Tree] = list()
    for o in branch.commit.tree.traverse(depth=1):
        if type(o) == git.objects.Tree:
            dirs.append(o)
        elif type(o) == git.objects.Blob:
            files.append(o)

    return render(request, "repo_detail.html", {
        "namespace":      db_repository.owner.username,
        "slug":           db_repository.slug,
        "branches":       branches,
        "current_branch": branch,
        "dirs":           dirs,
        "files":          files
    })


@login_required
def repo_listing(request, namespace: str, slug: str, ref: str, path: str):
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
    commit = repo.commit(ref)
    try:
        obj = commit.tree.join(path)
    except KeyError:
        raise Http404(f"Path {path} not found in repo {namespace}/{slug}")
    ty: str
    if type(obj) == git.objects.Tree:
        ty = "dir"
        files: list[git.objects.Blob] = list()
        dirs: list[git.objects.Tree] = list()
        for o in obj.traverse(depth=1):
            if type(o) == git.objects.Tree:
                dirs.append(o)
            elif type(o) == git.objects.Blob:
                files.append(o)
        o = {
            "files": files,
            "dirs":  dirs
        }
    elif type(obj) == git.objects.Blob:
        ty = "file"
        if "/" in path:
            [_, filename] = path.rsplit("/", 1)
        else:
            filename = path
        o = {
            "contents": obj.data_stream.read().decode('UTF-8'),
            "filename": filename
        }
    else:
        ty = "invalid"
        o = "invalid"
    if "/" in path:
        [base, _file] = path.rsplit("/", 1)
        kwargs = {
            "namespace":   namespace,
            "slug":        slug,
            "ref": ref,
            "path":        base
        }
        back_url = reverse("repo_listing", kwargs=kwargs)
    else:
        kwargs = {
            "namespace": namespace,
            "slug":      slug,
        }
        back_url = reverse("repo_detail", kwargs=kwargs)

    return render(request, "repo_listing.html", {
        "namespace":   db_repository.owner.username,
        "slug":        db_repository.slug,
        "path":        path,
        "ref": ref,
        "ty":          ty,
        "obj":         o,
        "back_url":    back_url
    })


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


@login_required
def new_repo(request: WSGIRequest):
    if request.method == "POST":
        form = NewRepoForm(request.POST)
        if form.is_valid():
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
