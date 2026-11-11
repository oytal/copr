# AGENTS.md

RPM packaging for Fedora COPR. One directory per package, built from this
repo (`github.com/oytal/copr`). Every package is in the shared COPR project
`oytal/oytal`; packages with `STANDALONE=yes` also have their own `oytal/<pkg>`.

To add a new package, follow `.claude/skills/add-package/SKILL.md` step by step.

## Layout

```
<pkg>/<pkg>.spec        spec file; directory name = spec name = RPM Name
<pkg>/package.env       UPSTREAM=owner/repo, TAG_PREFIX=v, ENABLE_NET=on|off,
                        optional TRACK=tags, STANDALONE=yes
templates/              go.spec, rust.spec, package.env.example to start from
test-build.sh           ./test-build.sh <pkg> [44 45 rawhide]: local build in podman
copr-setup.sh           ./copr-setup.sh <pkg>: add the package to the COPR project(s)
.github/workflows/bump.yml   hourly bumps specs to upstream's latest release
```

## Spec conventions

- `Source0` must be a URL containing `%{version}`. COPR downloads it with
  spectool, and the bump workflow only edits `Version:`, `Release:` and
  `%changelog`. Nothing else in the spec may hardcode the version.
- `Version:` is the upstream tag minus `TAG_PREFIX`. `Release: 1%{?dist}`.
  The tag prefix in the Source0 URL (`refs/tags/v%{version}`) must match
  `TAG_PREFIX` in `package.env`; change both together.
- Automatic bumps track GitHub *releases* (not prereleases). For upstreams
  that only push version tags set `TRACK=tags` (newest `TAG_PREFIX<x.y.z>`
  tag; tags with a `-` suffix are skipped). For upstreams with neither,
  leave `UPSTREAM=` empty and bump by hand.
- An app split over several upstream repos is several packages, one
  directory each (herdr, herdr-core, herdr-app); link them with
  `Requires:`. They all land in `oytal/oytal`.
- `STANDALONE=yes` only when the owner asks for a separate project.
- Upstreams with git submodules: GitHub tarballs leave them out. Fetch the
  pinned commit in `%prep` (see `herdr-core/herdr-core.spec`), not with a
  hardcoded commit in the spec.
- The COPR project descriptions list each package's `Summary:` and link to
  upstream: `https://github.com/$UPSTREAM`, or the spec's `URL:` when
  `UPSTREAM` is empty. In that case write `URL:` without macros so the link
  resolves. After changing either, the owner runs
  `./copr-setup.sh --update-description`.
- Changelog author: `oytal COPR <noreply@localhost>`, date from
  `date '+%a %b %d %Y'`.
- Plain `%changelog` entries (no `%autochangelog`/`%autorelease`). The bump
  workflow adds entries with `rpmdev-bumpspec`.
- BuildRequires as `pkgconfig(...)` where possible; runtime tools that are
  optional go in `Recommends:`.
- `ExclusiveArch: x86_64 aarch64` (the arches the COPR projects build).
- `%check` runs a smoke test that needs no TTY or network, such as `--version`.
- Install upstream's desktop file and icons if they exist; validate the
  desktop file with `desktop-file-validate` in `%check`.
- Language builds that download dependencies (Go, Rust, npm) need
  `ENABLE_NET=on` in `package.env`.
- Every target Fedora release must have the required compiler version. Check with
  `curl -s https://mdapi.fedoraproject.org/f44/pkg/golang` (or `rust`, etc).

## Fixing an existing package

When a build breaks (often right after the bump workflow moved to a new
upstream version): fix the spec, increment `Release:` (2, 3, ...), add a
`%changelog` entry for the same version, and run the full test build.
Never change `Version:` to something upstream has not released.

Read-only COPR commands are always fine for diagnosis:

```sh
copr-cli list-builds oytal/oytal          # status of recent builds
copr-cli get-package oytal/oytal --name <pkg> --with-latest-build
copr-cli status <build-id>
```

Build logs (chroot e.g. `fedora-44-x86_64`):
`https://download.copr.fedorainfracloud.org/results/oytal/oytal/<chroot>/<build-id>-<pkg>/builder-live.log.gz`
(standalone projects: `oytal/<pkg>` instead of `oytal/oytal`)

## Environment

Agents run on the owner's Arch machine. `podman`, `gh` and `copr-cli`
(configured in `~/.config/copr`) all work there; rpm tools
(`rpmlint`, `rpmspec`, `rpmdev-bumpspec`) are not installed. Use them
inside a `registry.fedoraproject.org/fedora:<rel>` container (or just
`test-build.sh`). Clone upstream sources into a scratch dir outside the repo.

## Rules for agents

- A package is done only when `./test-build.sh <pkg> 44 45 rawhide` passes.
  Read `<pkg>/.build/<rel>/rpmlint.txt` and fix real errors. Fine to ignore:
  missing manpages, and `spelling-error` on tool/project names (it reports
  those as E: on some releases).
- Do not commit or push. The owner signs commits and pushes themselves.
- Do not run `copr-setup.sh` or other `copr-cli` commands that change
  anything unless the owner asks. They change public projects.
- Add the package to the table in `README.md`.
- Finish by listing the owner's manual steps: commit and push, run
  `./copr-setup.sh <pkg>` (a webhook is only needed for a newly created
  project).
