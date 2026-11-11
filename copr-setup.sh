#!/usr/bin/env bash
# One-time setup of the COPR project for one package: ./copr-setup.sh <pkg>
# Refresh description/instructions of an existing project:
#   ./copr-setup.sh <pkg> --update-description
# Creates the COPR project oytal/<pkg> that builds from <pkg>/ in this repo.
#
# Several packages can share one project: a package whose package.env sets
# COPR_PROJECT=<pkg> is a member of <pkg>'s project. Setting up <pkg> also
# adds and builds its members. ./copr-setup.sh <member> adds just that
# member to the existing project.
# Needs ~/.config/copr from https://copr.fedorainfracloud.org/api/
set -euo pipefail

PKG=${1:?usage: $0 <package-dir> [--update-description]}
CLONE_URL=${CLONE_URL:-https://github.com/oytal/copr.git}
# Rawhide + --follow-fedora-branching: COPR adds new fedora-N chroots itself
CHROOTS=${CHROOTS:-fedora-44-x86_64 fedora-44-aarch64 fedora-45-x86_64 fedora-45-aarch64 fedora-rawhide-x86_64 fedora-rawhide-aarch64}

cd "$(dirname "$0")"
[ -f "$PKG/$PKG.spec" ] || { echo "missing $PKG/$PKG.spec" >&2; exit 1; }

# Reads <pkg>/package.env in a subshell and prints one variable
env_var() {
  (ENABLE_NET=off UPSTREAM= COPR_PROJECT=; [ -f "$1/package.env" ] && . "./$1/package.env"; eval "echo \"\${$2}\"")
}

# Adds <pkg> to <project> as an SCM package and starts its first build
add_package() {
  copr-cli add-package-scm "$2" \
    --name "$1" \
    --clone-url "$CLONE_URL" \
    --commit main \
    --subdir "$1" \
    --spec "$1.spec" \
    --type git \
    --method rpkg \
    --webhook-rebuild on
  copr-cli build-package "$2" --name "$1"
}

PROJECT=$(env_var "$PKG" COPR_PROJECT)
if [ -n "$PROJECT" ] && [ "$PROJECT" != "$PKG" ]; then
  [ "${2:-}" != --update-description ] || { echo "$PKG is in project $PROJECT: run $0 $PROJECT --update-description" >&2; exit 1; }
  add_package "$PKG" "$PROJECT"
  exit
fi

# Packages that share this project
members=()
for envfile in */package.env; do
  m=$(dirname "$envfile")
  [ "$m" != "$PKG" ] && [ "$(env_var "$m" COPR_PROJECT)" = "$PKG" ] && members+=("$m")
done

upstream_link() {
  local up url
  up=$(env_var "$1" UPSTREAM)
  # Upstream link: GitHub repo from package.env, else the spec URL if it has no macros
  if [ -n "$up" ]; then
    url="https://github.com/$up"
  else
    url=$(sed -n 's/^URL:[[:space:]]*//p' "$1/$1.spec" | grep -v '%' | head -1 || true)
  fi
  [ -z "$url" ] || echo "[$url]($url)"
}

summary=$(sed -n 's/^Summary:[[:space:]]*//p' "$PKG/$PKG.spec" | head -1)
description="$PKG: ${summary:-$PKG}."
if [ ${#members[@]} -eq 0 ]; then
  link=$(upstream_link "$PKG")
  [ -n "$link" ] && description+=$'\n\n'"Upstream: $link"
  description+=$'\n\n'"Packaging: [${CLONE_URL%.git}/tree/main/$PKG](${CLONE_URL%.git}/tree/main/$PKG)"
else
  description+=$'\n\n'"Packages:"
  for p in "$PKG" "${members[@]}"; do
    s=$(sed -n 's/^Summary:[[:space:]]*//p' "$p/$p.spec" | head -1)
    link=$(upstream_link "$p")
    description+=$'\n'"- **$p**: $s.${link:+ Upstream: $link.} Packaging: [$p](${CLONE_URL%.git}/tree/main/$p)"
  done
fi
instructions="sudo dnf copr enable oytal/$PKG && sudo dnf install $PKG${members[*]:+ ${members[*]}}"

if [ "${2:-}" = --update-description ]; then
  copr-cli modify "$PKG" --description "$description" --instructions "$instructions"
  exit
fi

# Any package of the project that downloads at build time needs network
net=off
for p in "$PKG" "${members[@]}"; do
  [ "$(env_var "$p" ENABLE_NET)" = on ] && net=on
done

chroot_args=()
for c in $CHROOTS; do chroot_args+=(--chroot "$c"); done

copr-cli create "$PKG" "${chroot_args[@]}" \
  --enable-net "$net" \
  --follow-fedora-branching on \
  --description "$description" \
  --instructions "$instructions"

for p in "$PKG" "${members[@]}"; do
  add_package "$p" "$PKG"
done
