# COPR packaging

RPM packaging for [Fedora COPR](https://copr.fedorainfracloud.org). Each
directory is one package, and each package has its own COPR project
`oytal/<package>`, built for Fedora 44, 45 and rawhide (x86_64 + aarch64).

| Package | Upstream | Install |
|---|---|---|
| cliamp | [bjarneo/cliamp](https://github.com/bjarneo/cliamp) | `sudo dnf copr enable oytal/cliamp && sudo dnf install cliamp` |

## Layout

```
<pkg>/<pkg>.spec    the spec file
<pkg>/package.env   UPSTREAM=<owner/repo> to track, ENABLE_NET=on|off
copr-setup.sh       one-time COPR project setup for a package
.github/workflows/bump.yml
```

## Automatic builds

1. `bump.yml` runs every 6 hours. For each `*/package.env` it compares the
   spec version with the latest stable GitHub release of `UPSTREAM`, bumps
   the spec (new version, release 1, changelog entry) and commits.
2. The push fires each COPR project's webhook. COPR rebuilds a package only
   when its subdirectory changed.

## Adding a package

1. Create `<pkg>/<pkg>.spec` and `<pkg>/package.env`. Source0 must be a URL,
   because COPR downloads it with spectool.
2. Test it locally (below), commit and push.
3. Run `./copr-setup.sh <pkg>` (needs `~/.config/copr` from
   <https://copr.fedorainfracloud.org/api/>).
4. In COPR open `oytal/<pkg>` → Settings → Integrations, copy the GitHub
   webhook URL and add it in this repo under Settings → Webhooks (content
   type `application/json`, push events only). Every COPR project needs its
   own webhook here.

## Fedora releases

Projects are created with rawhide chroots and `--follow-fedora-branching on`,
so when Fedora branches a new release from rawhide, COPR creates its chroots
automatically as forks of the rawhide chroots, built packages included. To
rebuild against the new release anyway:

```sh
copr-cli build-package <pkg> --name <pkg>
```

To drop an EOL release (`--chroot` replaces the whole list):

```sh
copr-cli modify <pkg> \
  --chroot fedora-45-x86_64 --chroot fedora-45-aarch64 \
  --chroot fedora-46-x86_64 --chroot fedora-46-aarch64 \
  --chroot fedora-rawhide-x86_64 --chroot fedora-rawhide-aarch64
```

Rawhide builds fail now and then when rawhide itself is broken. That does
not affect the stable release repos.

## Local test build

```sh
pkg=cliamp
podman run --rm -v $PWD/$pkg:/src:Z,ro registry.fedoraproject.org/fedora:44 bash -c "
  dnf -y install rpm-build rpmdevtools dnf-plugins-core &&
  rpmdev-setuptree && cp /src/$pkg.spec ~/rpmbuild/SPECS/ &&
  cd ~/rpmbuild/SPECS && spectool -g -R $pkg.spec &&
  dnf -y builddep $pkg.spec && rpmbuild -ba $pkg.spec"
```
