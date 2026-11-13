#!/usr/bin/env bash
# Build a package locally in clean Fedora containers, the way COPR would.
#   ./test-build.sh <pkg> [release ...]     e.g. ./test-build.sh cliamp 44 45 rawhide
# Default release: 44. RPMs and rpmlint output land in <pkg>/.build/<release>/.
set -euo pipefail

PKG=${1:?usage: $0 <pkg> [release ...]}
shift
RELEASES=${*:-44}

cd "$(dirname "$0")"
[ -f "$PKG/$PKG.spec" ] || { echo "missing $PKG/$PKG.spec" >&2; exit 1; }

# rpmbuild's BUILD dir (Rust target dirs reach many GB) goes to a host
# directory instead of the container's storage; set BUILD_ROOT to move it.
BUILD_ROOT=${BUILD_ROOT:-/var/tmp/copr-test-build}
# CARGO_BUILD_JOBS=2 ./test-build.sh <pkg> limits parallel rustc jobs (memory)
jobs_env=()
[ -n "${CARGO_BUILD_JOBS:-}" ] && jobs_env=(-e CARGO_BUILD_JOBS)

for rel in $RELEASES; do
  out="$PWD/$PKG/.build/$rel"
  work="$BUILD_ROOT/$PKG-$rel"
  rm -rf "$work"
  mkdir -p "$out" "$work"
  echo "==> $PKG on fedora:$rel (log: $out/build.log)"
  if ! podman run --rm -e PKG="$PKG" "${jobs_env[@]}" \
      -v "$PWD/$PKG:/src:Z,ro" -v "$out:/out:Z" -v "$work:/root/rpmbuild/BUILD:Z" \
      "registry.fedoraproject.org/fedora:$rel" bash -euc '
        dnf -y -q install rpm-build rpmdevtools dnf-plugins-core rpmlint >/dev/null 2>&1
        rpmdev-setuptree
        cp -r /src/. ~/rpmbuild/SOURCES/ && rm -rf ~/rpmbuild/SOURCES/.build
        cp /src/$PKG.spec ~/rpmbuild/SPECS/
        cd ~/rpmbuild/SPECS
        spectool -g -R $PKG.spec
        dnf -y -q builddep $PKG.spec >/dev/null 2>&1
        rpmbuild -ba $PKG.spec
        cp ~/rpmbuild/RPMS/*/*.rpm ~/rpmbuild/SRPMS/*.rpm /out/
        rpmlint /out/*.rpm > /out/rpmlint.txt 2>&1 || true
        echo "--- files"; rpm -qpl /out/*.$(uname -m).rpm
        echo "--- requires"; rpm -qpR /out/*.$(uname -m).rpm | grep -v "^rpmlib(" || true
      ' > "$out/build.log" 2>&1; then
    echo "FAILED on fedora:$rel, last lines of $out/build.log:" >&2
    tail -30 "$out/build.log" >&2
    podman unshare rm -rf "$work"
    exit 1
  fi
  podman unshare rm -rf "$work"
  sed -n '/^--- files/,$p' "$out/build.log"
  echo "--- rpmlint: $(tail -1 "$out/rpmlint.txt")"
done
echo "OK: $PKG built on: $RELEASES"
