# Electron app: the bundled binaries are upstream's, so no debuginfo or stripping
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs %{nil}
# Libraries shipped inside the app directory are not system provides
%global __provides_exclude_from ^%{_libdir}/bitwarden/.*$
# (libc.musl comes from the musl prebuilds of some npm modules, unused here)
%global __requires_exclude ^(libffmpeg|libEGL|libGLESv2|libvk_swiftshader|libvulkan|libprocess_isolation|libc\\.musl-[a-z0-9_]+)\\.so.*$

# Architecture names used by upstream's native module file names
%ifarch aarch64
%global napi_arch arm64
%else
%global napi_arch x64
%endif

Name:           bitwarden-desktop
Version:        2026.10.4
Release:        1%{?dist}
Summary:        Desktop client for the Bitwarden password manager

License:        GPL-3.0-only
URL:            https://github.com/bitwarden/clients
# The tag prefix is TAG_PREFIX in package.env; change both together
Source0:        %{url}/archive/refs/tags/desktop-v%{version}.tar.gz#/clients-desktop-v%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  nodejs24 >= 24.17
BuildRequires:  nodejs24-npm
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  git-core
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig(libsecret-1)
BuildRequires:  pkgconfig(xscrnsaver)

Requires:       polkit
Recommends:     libsecret
Recommends:     gnome-keyring

%description
Bitwarden is an open source password manager. This is its desktop app: it
stores logins, cards, identities and notes in an end-to-end encrypted vault
that syncs with the Bitwarden cloud or a self-hosted server. It also provides
the SSH agent, biometric unlock and browser integration (native messaging).

%prep
%autosetup -n clients-desktop-v%{version}

%build
# Dependencies come from the lockfiles, so this needs network access
npm ci --no-audit --no-fund

# The webpack bundles (JavaScript only) build while Cargo compiles the native
# parts, as they do not depend on each other
(cd apps/desktop && npm run build) > webpack.log 2>&1 &
webpack_pid=$!

# Native Rust modules. This is what desktop_native/build.js does for Linux,
# but as one Cargo run, so the crates shared by the three build once and in
# parallel instead of three times in a row.
pushd apps/desktop/desktop_native
cargo build --release -p desktop_napi -p desktop_proxy -p process_isolation
mkdir -p dist
cp target/release/libdesktop_napi.so napi/desktop_napi.linux-%{napi_arch}-gnu.node
cp target/release/desktop_proxy dist/desktop_proxy.linux-%{napi_arch}
cp target/release/libprocess_isolation.so dist/libprocess_isolation.so
popd

wait $webpack_pid || { cat webpack.log; exit 1; }
cat webpack.log

# An unpacked Electron app (no deb/rpm/snap target)
(cd apps/desktop && npm run pack:dir)

%install
appdir=$(echo apps/desktop/dist/linux*-unpacked)
install -d %{buildroot}%{_libdir}/bitwarden
cp -a "$appdir"/. %{buildroot}%{_libdir}/bitwarden/
# The launcher script resolves symlinks to find the app directory
install -d %{buildroot}%{_bindir}
ln -s %{_libdir}/bitwarden/bitwarden %{buildroot}%{_bindir}/bitwarden

install -Dpm 0644 apps/desktop/resources/com.bitwarden.desktop.desktop \
    %{buildroot}%{_datadir}/applications/com.bitwarden.desktop.desktop
for size in 16 32 64 128 256 512 1024; do
    install -Dpm 0644 apps/desktop/resources/icons/${size}x${size}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/com.bitwarden.desktop.png
done
install -Dpm 0644 apps/desktop/resources/com.bitwarden.desktop.policy \
    %{buildroot}%{_datadir}/polkit-1/actions/com.bitwarden.desktop.policy

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.bitwarden.desktop.desktop
# Starting Electron needs a display, so only check the app is complete
test -x %{buildroot}%{_libdir}/bitwarden/bitwarden
test -x %{buildroot}%{_libdir}/bitwarden/bitwarden-app
test -f %{buildroot}%{_libdir}/bitwarden/resources/app.asar
test -f %{buildroot}%{_libdir}/bitwarden/desktop_proxy

%files
%license LICENSE_GPL.txt
%doc apps/desktop/README.md
%{_bindir}/bitwarden
%{_libdir}/bitwarden/
%{_datadir}/applications/com.bitwarden.desktop.desktop
%{_datadir}/icons/hicolor/*/apps/com.bitwarden.desktop.png
%{_datadir}/polkit-1/actions/com.bitwarden.desktop.policy

%changelog
* Fri Nov 13 2026 oytal COPR <noreply@localhost> - 2026.10.4-1
- Initial COPR package
