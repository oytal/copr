---
name: add-package
description: Package a new application for COPR in this repo. Use when asked to add, package or create a COPR build for an app (usually given a GitHub URL).
---

# Add a package to the COPR repo

Input: an upstream project, usually a GitHub URL. Follow the conventions in
`AGENTS.md`. Work through these steps in order.

## 1. Research upstream

Clone it shallowly into a scratch directory outside this repo (`mktemp -d`):

```sh
gh api repos/<owner>/<repo> --jq '{lang:.language,license:.license.spdx_id,desc:.description}'
gh api repos/<owner>/<repo>/releases/latest --jq '{tag:.tag_name,pre:.prerelease}'
git clone --depth 1 --branch <tag> https://github.com/<owner>/<repo> <scratch>/<repo>
```

Find out:
- **Build system and toolchain version.** Look at go.mod `go` line,
  rust-version in Cargo.toml, package.json engines, and so on. Check that
  Fedora 44, 45 and rawhide ship that version:
  `curl -s https://mdapi.fedoraproject.org/f44/pkg/<golang|rust|nodejs>`.
- **Exact build command.** Upstream's Makefile, `.github/workflows/release*`,
  AUR PKGBUILD workflow, flake.nix or goreleaser config. Copy their ldflags
  (version injection) and build tags.
- **C library dependencies.** Look for cgo `#include`, `pkg-config` in
  build.rs/-sys crates, README "building from source", and upstream's
  apt/dnf/pacman install lines. Map them to Fedora `pkgconfig(...)` names
  (`dnf repoquery --whatprovides 'pkgconfig(x)'` in a fedora container).
- **Runtime tools** that the app calls (ffmpeg, yt-dlp, and so on): these
  become `Recommends:`. Find out whether a sound or display bridge is needed.
- **Files to install.** Binary name, desktop file, icons (png size, svg),
  man pages, shell completions, LICENSE, README.
- **Tag format**, for `TAG_PREFIX`, and the top directory of the source
  tarball (`<repo>-<version>`), for `%autosetup -n`.

## 2. Write the files

```sh
mkdir <pkg>
cp templates/<go|rust>.spec <pkg>/<pkg>.spec     # or write from scratch for other languages
cp templates/package.env.example <pkg>/package.env
```

Replace every `TODO` (`grep -n TODO <pkg>/*` must come back empty). Use
`cliamp/cliamp.spec` as a working reference. Use today's date in the
changelog, in `date '+%a %b %d %Y'` format.

## 3. Build and fix

```sh
./test-build.sh <pkg> 44
```

Iterate until it passes, then run `./test-build.sh <pkg> 44 45 rawhide`.
Failures and fixes:
- Missing header/library: add the `pkgconfig(...)` BuildRequires.
- `%autosetup` dir not found: fix `-n` to match the tarball's top dir.
- Installed but unpackaged files: add them to `%files` or don't install them.
- Empty debuginfo / missing build-id: keep `%global debug_package %{nil}`.
- `%check` hangs or needs a TTY: use a non-interactive flag such as `--version`/`--help`.

Read `<pkg>/.build/<rel>/rpmlint.txt`: fix errors. Look at the `--- files`
and `--- requires` output: check the binary, desktop file and icons are
there and nothing unexpected is linked.

## 4. Finish

- Add a row to the package table in `README.md`.
- Commit it: `git add <pkg> README.md && git commit -m "Add <pkg>"`. Do not
  push without asking the owner, and do not run `copr-setup.sh`.
- Report the test results and give the owner the manual steps:
  1. Approve the push (or `git push` it themselves)
  2. `./copr-setup.sh <pkg>` (adds it to the public COPR project
     `oytal/oytal` and starts the first build)
  3. Only if the package has `STANDALONE=yes` (a new project `oytal/<pkg>`):
     COPR `oytal/<pkg>` → Settings → Integrations: copy the GitHub webhook
     URL and add it at github.com/oytal/copr → Settings → Webhooks
     (`application/json`, push events only).
