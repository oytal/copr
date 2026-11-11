#!/usr/bin/env bash
# Puts packages from this repo on COPR. Safe to re-run.
#   ./copr-setup.sh <pkg>...                  add/update <pkg> in oytal/oytal and build it
#   ./copr-setup.sh --all                     the same for every package
#   ./copr-setup.sh --update-description      refresh project descriptions only
#
# Every package builds in one shared project, oytal/$MAIN. A package whose
# package.env sets STANDALONE=yes also gets a project of its own, oytal/<pkg>,
# for people who want just that app. The first run creates the projects.
# Needs ~/.config/copr from https://copr.fedorainfracloud.org/api/
set -euo pipefail

MAIN=${MAIN:-oytal}
OWNER=${OWNER:-oytal}
CLONE_URL=${CLONE_URL:-https://github.com/oytal/copr.git}
REPO_URL=${CLONE_URL%.git}
# Rawhide + --follow-fedora-branching: COPR adds new fedora-N chroots itself
CHROOTS=${CHROOTS:-fedora-44-x86_64 fedora-44-aarch64 fedora-45-x86_64 fedora-45-aarch64 fedora-rawhide-x86_64 fedora-rawhide-aarch64}

cd "$(dirname "$0")"

all_packages() {
  for envfile in */package.env; do dirname "$envfile"; done
}

# Prints one variable of <pkg>/package.env
env_var() {
  (ENABLE_NET=off UPSTREAM= STANDALONE=; . "./$1/package.env"; eval "echo \"\${$2}\"")
}

summary() { sed -n 's/^Summary:[[:space:]]*//p' "$1/$1.spec" | head -1; }

# Upstream URL: GitHub repo from package.env, else the spec URL if it has no macros
upstream_url() {
  local up
  up=$(env_var "$1" UPSTREAM)
  if [ -n "$up" ]; then echo "https://github.com/$up"
  else sed -n 's/^URL:[[:space:]]*//p' "$1/$1.spec" | grep -v '%' | head -1 || true
  fi
}

project_exists() { copr-cli list "$OWNER" 2>/dev/null | grep -qx "Name: $1"; }

# Description and install line of the shared project: every package
main_description() {
  local p url
  echo "Apps packaged by $OWNER for Fedora. Enable once, then install any of them."
  echo
  for p in $(all_packages); do
    url=$(upstream_url "$p")
    echo "- **$p**: $(summary "$p").${url:+ [Upstream]($url).} [Packaging]($REPO_URL/tree/main/$p)"
  done
}
main_instructions() { echo "sudo dnf copr enable $OWNER/$MAIN && sudo dnf install <package>"; }

# Description and install line of a standalone project
pkg_description() {
  local url
  url=$(upstream_url "$1")
  echo "$1: $(summary "$1")."
  [ -z "$url" ] || printf '\nUpstream: [%s](%s)\n' "$url" "$url"
  printf '\nPackaging: [%s](%s)\n' "$REPO_URL/tree/main/$1" "$REPO_URL/tree/main/$1"
  printf '\nAlso in %s/%s with the other apps from %s.\n' "$OWNER" "$MAIN" "$REPO_URL"
}
pkg_instructions() { echo "sudo dnf copr enable $OWNER/$1 && sudo dnf install $1"; }

# create_or_modify <project> <description> <instructions> <enable-net>
create_or_modify() {
  if project_exists "$1"; then
    copr-cli modify "$1" --description "$2" --instructions "$3" --enable-net "$4"
  else
    local chroot_args=() c
    for c in $CHROOTS; do chroot_args+=(--chroot "$c"); done
    copr-cli create "$1" "${chroot_args[@]}" \
      --enable-net "$4" \
      --follow-fedora-branching on \
      --description "$2" \
      --instructions "$3"
    echo "Created $OWNER/$1. Add its webhook: COPR → Settings → Integrations → GitHub URL," \
      "then $REPO_URL → Settings → Webhooks (application/json, push events)." >&2
  fi
}

# The shared project needs network if any package downloads at build time
main_net() {
  local p
  for p in $(all_packages); do [ "$(env_var "$p" ENABLE_NET)" = on ] && { echo on; return; }; done
  echo off
}

update_descriptions() {
  local p
  create_or_modify "$MAIN" "$(main_description)" "$(main_instructions)" "$(main_net)"
  for p in $(all_packages); do
    [ "$(env_var "$p" STANDALONE)" = yes ] && project_exists "$p" &&
      copr-cli modify "$p" --description "$(pkg_description "$p")" --instructions "$(pkg_instructions "$p")"
  done
  return 0
}

# add_package <pkg> <project>: add (or update) the SCM package, then build it
add_package() {
  local cmd=add-package-scm
  copr-cli get-package "$OWNER/$2" --name "$1" >/dev/null 2>&1 && cmd=edit-package-scm
  copr-cli "$cmd" "$2" \
    --name "$1" \
    --clone-url "$CLONE_URL" \
    --commit main \
    --subdir "$1" \
    --spec "$1.spec" \
    --type git \
    --method rpkg \
    --webhook-rebuild on
  copr-cli build-package "$2" --name "$1" --nowait
}

case "${1:-}" in
  "") echo "usage: $0 <pkg>... | --all | --update-description" >&2; exit 1 ;;
  --update-description) update_descriptions; exit ;;
  --all) set -- $(all_packages) ;;
esac
for p in "$@"; do
  [ -f "$p/$p.spec" ] && [ -f "$p/package.env" ] || { echo "missing $p/$p.spec or $p/package.env" >&2; exit 1; }
done

# Shared project first (its description lists every package)
update_descriptions
for p in "$@"; do
  add_package "$p" "$MAIN"
  if [ "$(env_var "$p" STANDALONE)" = yes ]; then
    create_or_modify "$p" "$(pkg_description "$p")" "$(pkg_instructions "$p")" "$(env_var "$p" ENABLE_NET)"
    add_package "$p" "$p"
  fi
done
