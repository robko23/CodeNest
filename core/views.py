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
from django.utils.text import slugify
from gitdb.exc import BadObject

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
            return render(request, "repo_empty.html", {
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

    return render(request, "repo_detail.html", {
        "namespace":       db_repository.owner.username,
        "slug":            db_repository.slug,
        "branches":        branches,
        "path":            path,
        "current_ref":     current_ref,
        "tree":            tree,
        "file":            file,
        "current_ref_str": current_ref_str,
        "back_url":        back_url
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
