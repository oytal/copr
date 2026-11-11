#!/usr/bin/env bash
# One-time setup of the COPR project for one package: ./copr-setup.sh <pkg>
# Refresh description/instructions of an existing project:
#   ./copr-setup.sh <pkg> --update-description
# Creates the COPR project oytal/<pkg> that builds from <pkg>/ in this repo.
# Needs ~/.config/copr from https://copr.fedorainfracloud.org/api/
set -euo pipefail

PKG=${1:?usage: $0 <package-dir>}
CLONE_URL=${CLONE_URL:-https://github.com/oytal/copr.git}
# Rawhide + --follow-fedora-branching: COPR adds new fedora-N chroots itself
CHROOTS=${CHROOTS:-fedora-44-x86_64 fedora-44-aarch64 fedora-45-x86_64 fedora-45-aarch64 fedora-rawhide-x86_64 fedora-rawhide-aarch64}

cd "$(dirname "$0")"
[ -f "$PKG/$PKG.spec" ] || { echo "missing $PKG/$PKG.spec" >&2; exit 1; }
ENABLE_NET=off
UPSTREAM=
[ -f "$PKG/package.env" ] && . "./$PKG/package.env"

summary=$(sed -n 's/^Summary:[[:space:]]*//p' "$PKG/$PKG.spec" | head -1)
# Upstream link: GitHub repo from package.env, else the spec URL if it has no macros
if [ -n "$UPSTREAM" ]; then
  upstream_url="https://github.com/$UPSTREAM"
else
  upstream_url=$(sed -n 's/^URL:[[:space:]]*//p' "$PKG/$PKG.spec" | grep -v '%' | head -1 || true)
fi
description="$PKG: ${summary:-$PKG}."
[ -n "$upstream_url" ] && description+=$'\n\n'"Upstream: [$upstream_url]($upstream_url)"
description+=$'\n\n'"Packaging: [${CLONE_URL%.git}/tree/main/$PKG](${CLONE_URL%.git}/tree/main/$PKG)"
instructions="sudo dnf copr enable oytal/$PKG && sudo dnf install $PKG"

if [ "${2:-}" = --update-description ]; then
  copr-cli modify "$PKG" --description "$description" --instructions "$instructions"
  exit
fi

chroot_args=()
for c in $CHROOTS; do chroot_args+=(--chroot "$c"); done

copr-cli create "$PKG" "${chroot_args[@]}" \
  --enable-net "$ENABLE_NET" \
  --follow-fedora-branching on \
  --description "$description" \
  --instructions "$instructions"

copr-cli add-package-scm "$PKG" \
  --name "$PKG" \
  --clone-url "$CLONE_URL" \
  --commit main \
  --subdir "$PKG" \
  --spec "$PKG.spec" \
  --type git \
  --method rpkg \
  --webhook-rebuild on

copr-cli build-package "$PKG" --name "$PKG"
