# CodeNest

A simple git server implementation that was made as a uni project for python course

# Running this

Ensure you have [Taskfile](https://taskfile.dev/installation/)
and [Docker](https://docs.docker.com/engine/install/) with buildx plugin.

Development is being done on linux machine and I don't care if it does not work on Windows. Get a
linux machine :)

Once you have installed those two things, running is as simple as `task run`

# Roadmap/TODOs

- [x] repo creation
- [x] ssh keys creation
- [ ] dev container (git hooks depend on openssh, so we need a way to run `manage.py runserver`
  inside the container with openssh-server running to test things)
- [ ] repo deletion
- [ ] nicer ui + homepage
- [ ] registration/forgot password and other django login pages
- [ ] issues
- [ ] commit-issue linking?