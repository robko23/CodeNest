# Create your views here.
import logging

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from core.forms import NewRepoForm
from core.forms import NewSSHKeyForm
from core.models import Repository
from core.models import SSHKey
from core.util.git import create_git_repo
from core.util.ssh import get_pubkey_fingerprint

log = logging.getLogger(__name__)


@login_required
def home(request: WSGIRequest):
    ssh_keys = SSHKey.objects.filter(owner=request.user)
    repos = Repository.objects.filter(owner=request.user)
    return render(request, "home.html", {
        'ssh_keys': ssh_keys,
        'repos':    repos
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
