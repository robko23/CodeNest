# CodeNest

A simple git server implementation that was made as a uni project for python course

# Running this

Ensure you have [Taskfile](https://taskfile.dev/installation/)
and [Docker](https://docs.docker.com/engine/install/) with buildx plugin.

Development is being done on linux machine and I don't care if it does not work on Windows. Get a
linux machine :)

Once you have installed those two things, running is as simple as `task run`.

To run `manage.py runserver` and develop inside the container, just run `task run-dev`

# Pushing real git repo to CodeNest

Once you managed to run this, generate a test key with `task make-test-keys`.

Then you need to create user in django (`manage.py createsuperuser`), create repository and add
public ssh key (found
in `<codenest-path>/test_key.pub`) - this in done in app (`http://localhost:8080/`).

Next you initialize normal git repo somewhere with `git init`.

Local ssh server runs on port 2222,
so you need to tell git to use that port and to use your private key.
This is done with command

```
git config core.sshCommand "ssh -p 2222 -i <codenest-path>/test_key"
```

Add remote

```
git remote add origin git@localhost:<username>/<slug>
```

And finally you can push with `git push origin main`

# Roadmap/TODOs

- [x] repo creation
- [x] ssh keys creation
- [x] dev container (git hooks depend on openssh, so we need a way to run `manage.py runserver`
  inside the container with openssh-server running to test things)
- [x] [fix git hooks creation](https://github.com/robko23/CodeNest/issues/1)
- [x] [fix push authentication - we need env vars for django to work + we are using in-memory cache,
  use memcached or redis?](https://github.com/robko23/CodeNest/issues/2)
- [x] [repo deletion](https://github.com/robko23/CodeNest/issues/3)
- [x] [nicer ui + homepage](https://github.com/robko23/CodeNest/issues/4)
- [x] [registration/forgot password and other django login pages](https://github.com/robko23/CodeNest/issues/5)
- [x] issues
