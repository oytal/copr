# COPR packaging

RPM packaging for [Fedora COPR](https://copr.fedorainfracloud.org), built
for Fedora 44, 45 and rawhide (x86_64 + aarch64). Each directory is one
package. All of them build in one COPR project, `oytal/oytal`:

```sh
sudo dnf copr enable oytal/oytal
sudo dnf install <package>
```

A few packages also have a project of their own (`STANDALONE=yes` in
`package.env`), for people who want just that app.

| Package | Upstream | Own project |
|---|---|---|
| cliamp | [bjarneo/cliamp](https://github.com/bjarneo/cliamp) | `oytal/cliamp` |
| herdr | [herdrdev/herdr](https://github.com/herdrdev/herdr) | |
| herdr-app | [herdrdev/herdr-app](https://github.com/herdrdev/herdr-app) | |
| herdr-core | [herdrdev/herdr-core](https://github.com/herdrdev/herdr-core) | |
| kubie | [kubie-org/kubie](https://github.com/kubie-org/kubie) | |

## Layout

```
<pkg>/<pkg>.spec    the spec file
<pkg>/package.env   UPSTREAM=<owner/repo> to track, TAG_PREFIX, ENABLE_NET=on|off,
                    optional TRACK=tags, STANDALONE=yes
templates/          starter specs (Go, Rust) and package.env.example
test-build.sh       local build in Fedora containers
copr-setup.sh       adds packages to the COPR projects (safe to re-run)
AGENTS.md           conventions for coding agents (CLAUDE.md imports it)
.claude/skills/add-package/SKILL.md   step-by-step "package a new app"
.github/workflows/bump.yml
```

Agents: ask for "add <github url> as a new package". The add-package skill
covers research, spec, test builds and the manual steps left for you.

## Automatic builds

1. `bump.yml` runs every hour. For each `*/package.env` it compares the
   spec version with the latest stable GitHub release of `UPSTREAM` (or,
   with `TRACK=tags`, its newest `TAG_PREFIX<x.y.z>` tag), bumps
   the spec (new version, release 1, changelog entry) and commits.
2. The push fires the COPR webhooks (`oytal/oytal` and each standalone
   project). COPR rebuilds a package only when its subdirectory changed.

## Adding a package

1. Create `<pkg>/<pkg>.spec` and `<pkg>/package.env`, starting from
   `templates/`. Source0 must be a URL, because COPR downloads it with
   spectool.
2. Test it with `./test-build.sh <pkg> 44 45 rawhide`, then commit and push.
3. Run `./copr-setup.sh <pkg>` (needs `~/.config/copr` from
   <https://copr.fedorainfracloud.org/api/>). It adds the package to
   `oytal/oytal` and starts a build; with `STANDALONE=yes` it also creates
   `oytal/<pkg>` and builds it there.
4. Only when step 3 created a project (the first `oytal/oytal` run, or a
   new standalone project): in COPR open it → Settings → Integrations, copy
   the GitHub webhook URL and add it in this repo under Settings → Webhooks
   (content type `application/json`, push events only). Each project needs
   its own webhook; one covers all packages in it.

`./copr-setup.sh --all` does the same for every package.

To refresh the project descriptions (package list, summaries, upstream and
packaging links) after changing a spec or `package.env`:

```sh
./copr-setup.sh --update-description
```

## Fedora releases

Projects are created with rawhide chroots and `--follow-fedora-branching on`,
so when Fedora branches a new release from rawhide, COPR creates its chroots
automatically as forks of the rawhide chroots, built packages included. To
rebuild against the new release anyway:

```sh
copr-cli build-package oytal --name <pkg>
```

To drop an EOL release (`--chroot` replaces the whole list; repeat for each
standalone project):

```sh
copr-cli modify oytal \
  --chroot fedora-45-x86_64 --chroot fedora-45-aarch64 \
  --chroot fedora-46-x86_64 --chroot fedora-46-aarch64 \
  --chroot fedora-rawhide-x86_64 --chroot fedora-rawhide-aarch64
```

Rawhide builds fail now and then when rawhide itself is broken. That does
not affect the stable release repos.

## Local test build

```sh
./test-build.sh cliamp                  # Fedora 44
./test-build.sh cliamp 44 45 rawhide    # all targets
```

RPMs, the build log and rpmlint output end up in `<pkg>/.build/<release>/`
(git-ignored).
