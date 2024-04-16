# CodeNest

A simple git server implementation that was made as a uni project for python course

# Running this

Ensure you have [Taskfile](https://taskfile.dev/installation/)
and [Docker](https://docs.docker.com/engine/install/) with buildx plugin.

Development is being done on linux machine and I don't care if it does not work on Windows. Get a
linux machine :)

Once you have installed those two things, running is as simple as `task run`.

To run `manage.py runserver` and develop inside the container, just run `task run-dev`

# Roadmap/TODOs

- [x] repo creation
- [x] ssh keys creation
- [x] dev container (git hooks depend on openssh, so we need a way to run `manage.py runserver`
  inside the container with openssh-server running to test things)
- [ ] [fix git hooks creation](https://github.com/robko23/CodeNest/issues/1)
- [ ] [fix push authentication - we need env vars for django to work + we are using in-memory cache,
  use memcached or redis?](https://github.com/robko23/CodeNest/issues/2)
- [ ] [repo deletion](https://github.com/robko23/CodeNest/issues/3)
- [ ] [nicer ui + homepage](https://github.com/robko23/CodeNest/issues/4)
- [ ] [registration/forgot password and other django login pages](https://github.com/robko23/CodeNest/issues/5)
- [ ] issues
- [ ] commit-issue linking?
