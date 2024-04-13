import pathlib
import subprocess

from django.conf import settings


def create_git_repo(path: str):
    absolute_path = settings.DATA_DIR / path

    # only for quicker development
    subprocess.run(['rm', '-rf', absolute_path])

    pathlib.Path(absolute_path).mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '--bare', absolute_path])

    subprocess.run(['rm', '-rf', absolute_path / "hooks"])

    subprocess.run(['ln', '-s', settings.GIT_HOOKS_DIR, absolute_path / "hooks"])
    pass
