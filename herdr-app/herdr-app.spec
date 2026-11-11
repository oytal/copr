# Rust GUI (gpui) linking libghostty-vt, which build.rs compiles with Zig from
# the vendor/ghostty git submodule. Cargo, Zig and %%prep (the submodule)
# download at build time, so the COPR project needs ENABLE_NET=on.
%global debug_package %{nil}

Name:           herdr-app
Version:        0.1.15
Release:        1%{?dist}
Summary:        Herdr desktop app: terminals and coding agents that keep running

# herdr-app is Apache-2.0; vendored gpui, taffy and libghostty-vt are
# Apache-2.0 or MIT (see THIRD-PARTY-NOTICES)
License:        Apache-2.0 AND MIT
URL:            https://github.com/herdrdev/herdr-app
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  zig >= 0.16
# bindgen for ghostty-sys
BuildRequires:  clang-devel
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xkbcommon-x11)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  desktop-file-utils
# %%prep fetches the vendor/ghostty submodule
BuildRequires:  git-core
BuildRequires:  curl
BuildRequires:  tar

# The app runs its terminals in herdr-core (hc); without it the app would
# download the core into ~/.local/bin
Requires:       herdr-core
Requires:       hicolor-icon-theme

%description
Herdr is a desktop app for terminals and coding agents that keep running
when the window closes. It shows the terminals of herdr-core (hc) in
workspaces with tabs and splits, and can be extended with mods.

%prep
%autosetup -n %{name}-%{version}
# vendor/ghostty is a git submodule, which GitHub tarballs leave out.
# Read the commit this tag pins and fetch that Ghostty source.
git clone -q --bare --depth 1 --filter=blob:none --branch v%{version} %{url}.git %{_builddir}/%{name}-gitlink
ghostty=$(git -C %{_builddir}/%{name}-gitlink rev-parse HEAD:vendor/ghostty)
rm -rf %{_builddir}/%{name}-gitlink
mkdir -p vendor/ghostty
curl -fsSL --retry 3 https://github.com/ghostty-org/ghostty/archive/$ghostty.tar.gz |
  tar -xz --strip-components=1 -C vendor/ghostty

%build
export CARGO_HOME=%{_builddir}/cargo
export ZIG_GLOBAL_CACHE_DIR=%{_builddir}/zig-cache
# Fedora sets -Cstrip=none (for debuginfo); strip here since debuginfo is off
export RUSTFLAGS="%{build_rustflags} -Cstrip=symbols"
# No HERDR_APP_RELEASE: that turns on the self-updater and telemetry, which
# upstream only enables in its own release builds
cargo build --release --locked -p herdr-app

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 assets/icons/herdr-ui-icon-clean.svg \
  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
# Upstream has no desktop file in the repo; this is the one scripts/install-linux writes
install -d %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{name}.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Herdr
Comment=Terminals and coding agents that keep running
Exec=herdr-app
Icon=herdr-app
Terminal=false
Categories=Development;
StartupWMClass=herdr-app
EOF

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
%{buildroot}%{_bindir}/%{name} --version

%files
%license LICENSE THIRD-PARTY-NOTICES
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%changelog
* Wed Nov 11 2026 oytal COPR <noreply@localhost> - 0.1.15-1
- Initial COPR package
