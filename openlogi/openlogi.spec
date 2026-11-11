# Rust workspace (GUI on gpui); Cargo fetches crates and git dependencies at
# build time, so the COPR project needs ENABLE_NET=on in package.env.
# Built like upstream's `cargo xtask linux package` (nfpm.yaml): same four
# binaries, udev rules, systemd user unit, desktop file and icons.
%global debug_package %{nil}

Name:           openlogi
Version:        0.9.0
Release:        1%{?dist}
Summary:        Local-first alternative to Logitech Options+ for HID++ devices

License:        Apache-2.0 OR MIT
URL:            https://github.com/AprilNEA/OpenLogi
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/OpenLogi-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

# Upstream's rust-version
BuildRequires:  rust >= 1.99
BuildRequires:  cargo
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  clang-devel
BuildRequires:  git-core
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xkbcommon-x11)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  desktop-file-utils
BuildRequires:  systemd-rpm-macros

Requires:       hicolor-icon-theme
# The udev rules grant the logged-in user access via logind's uaccess tag
Requires:       systemd-udev
%{?systemd_requires}

%description
OpenLogi configures Logitech mice and keyboards over HID++: remap buttons,
set DPI and SmartShift, without an account or telemetry. Configuration lives
in a plain TOML file.

It ships a desktop app (openlogi-desktop), a CLI (openlogi) and a background
agent that applies the settings. Enable the agent for your user with:

  systemctl --user enable --now openlogi-agent.service

%prep
%autosetup -n OpenLogi-%{version}

%build
export CARGO_HOME=%{_builddir}/cargo
# Fedora sets -Cstrip=none (for debuginfo); strip here since debuginfo is off
export RUSTFLAGS="%{build_rustflags} -Cstrip=symbols"
# Upstream's release profile uses fat LTO; four gpui binaries linked that way
# at once need far more memory than a build VM has (rustc gets OOM-killed).
# Thin LTO keeps cross-crate optimisation at a fraction of the memory.
export CARGO_PROFILE_RELEASE_LTO=thin
# No OPENLOGI_UPDATE_MINISIGN_PUBLIC_KEY: without it the in-app updater stays
# off, so updates come from dnf
# --bin, not -p: -p openlogi-agent would also build its test-only mock agent
cargo build --release --locked --workspace \
  --bin openlogi --bin openlogi-desktop --bin openlogi-overlay --bin openlogi-agent

%install
for bin in openlogi openlogi-desktop openlogi-overlay openlogi-agent; do
  install -Dpm 0755 target/release/$bin %{buildroot}%{_bindir}/$bin
done
install -Dpm 0644 packaging/linux/udev/70-openlogi.rules %{buildroot}%{_udevrulesdir}/70-openlogi.rules
install -Dpm 0644 packaging/linux/systemd/openlogi-agent.service %{buildroot}%{_userunitdir}/openlogi-agent.service
install -Dpm 0644 packaging/linux/desktop/openlogi.desktop %{buildroot}%{_datadir}/applications/openlogi.desktop
install -Dpm 0644 design/icon/openlogi.png %{buildroot}%{_datadir}/icons/hicolor/1024x1024/apps/openlogi.png
for size in 512 256 128 64 48 32 16; do
  install -Dpm 0644 design/icon/openlogi-$size.png \
    %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/openlogi.png
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/openlogi.desktop
%{buildroot}%{_bindir}/openlogi --version

%post
%systemd_user_post openlogi-agent.service
%udev_rules_update
# Apply the uaccess tags to devices that are already plugged in, as upstream's
# package does, so the agent can open them without a replug
if [ -x /usr/bin/udevadm ]; then
  udevadm trigger --subsystem-match=hidraw || :
  udevadm trigger --subsystem-match=input || :
  udevadm trigger --subsystem-match=misc --attr-match=name=uinput || :
fi

%preun
%systemd_user_preun openlogi-agent.service

%postun
%systemd_user_postun openlogi-agent.service
%udev_rules_update

%files
%license LICENSE-APACHE LICENSE-MIT
%doc README.md CHANGELOG.md
%{_bindir}/openlogi
%{_bindir}/openlogi-desktop
%{_bindir}/openlogi-overlay
%{_bindir}/openlogi-agent
%{_udevrulesdir}/70-openlogi.rules
%{_userunitdir}/openlogi-agent.service
%{_datadir}/applications/openlogi.desktop
%{_datadir}/icons/hicolor/*/apps/openlogi.png

%changelog
* Wed Nov 11 2026 oytal COPR <noreply@localhost> - 0.9.0-1
- Initial COPR package
