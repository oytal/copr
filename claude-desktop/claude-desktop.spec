# Prebuilt Electron app repackaged from Anthropic's official .deb: no
# debuginfo, no stripping
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs %{nil}
# Upstream installs under /usr/lib on every architecture, and its D-Bus
# service file refers to that path
%global appdir %{_prefix}/lib/claude-desktop
# Libraries shipped inside the app directory are not system provides
%global __provides_exclude_from ^%{appdir}/.*$
%global __requires_exclude ^(libffmpeg|libEGL|libGLESv2|libvk_swiftshader|libvulkan)\\.so.*$

Name:           claude-desktop
Version:        5.11492.2
Release:        1%{?dist}
Summary:        Desktop application for Claude.ai

# Proprietary, redistributed as published in Anthropic's apt repository.
# Use is subject to Anthropic's terms: https://www.anthropic.com/legal
License:        LicenseRef-Anthropic-Proprietary
URL:            https://claude.ai/download
# Anthropic publishes the Linux app only as a .deb in its apt repository
# (no GitHub releases): bump Version by hand, see package.env
%ifarch aarch64
Source0:        https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop/claude-desktop_%{version}_arm64.deb
%else
Source0:        https://downloads.claude.ai/claude-desktop/apt/stable/pool/main/c/claude-desktop/claude-desktop_%{version}_amd64.deb
%endif

ExclusiveArch:  x86_64 aarch64

# To unpack the .deb
BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme
Requires:       xdg-utils
Requires:       xdg-desktop-portal
Requires:       glib2
Recommends:     xdg-desktop-portal-gtk
Recommends:     libsecret
Recommends:     gnome-keyring
Recommends:     libappindicator-gtk3
Recommends:     gjs

%description
The desktop application for Claude, Anthropic's AI assistant. It provides
chat, Claude Code sessions, connectors and extensions in a native window.

This package repackages the official Linux release published in Anthropic's
apt repository.

%prep
%setup -q -c -T
ar x %{SOURCE0}
tar xf data.tar.*

%build
# Nothing to build: the release is a prebuilt Electron application

%install
install -d %{buildroot}%{appdir}
cp -a usr/lib/claude-desktop/. %{buildroot}%{appdir}/
install -d %{buildroot}%{_bindir}
ln -s ../lib/claude-desktop/claude-desktop %{buildroot}%{_bindir}/claude-desktop

install -Dpm 0644 usr/share/applications/com.anthropic.Claude.desktop \
    %{buildroot}%{_datadir}/applications/com.anthropic.Claude.desktop
for size in 16 32 48 128 256; do
    install -Dpm 0644 usr/share/icons/hicolor/${size}x${size}/apps/claude-desktop.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/claude-desktop.png
done

# What upstream's postinst registers on Debian systems: the GNOME Shell search
# provider and the MIME types for extensions and skills
sp=%{buildroot}%{appdir}/resources/gnome-search-provider
install -Dpm 0644 $sp/com.anthropic.Claude.search-provider.ini \
    %{buildroot}%{_datadir}/gnome-shell/search-providers/com.anthropic.Claude.search-provider.ini
install -Dpm 0644 $sp/com.anthropic.Claude.SearchProvider.service \
    %{buildroot}%{_datadir}/dbus-1/services/com.anthropic.Claude.SearchProvider.service
install -Dpm 0644 %{buildroot}%{appdir}/resources/linux-mime/com.anthropic.Claude.xml \
    %{buildroot}%{_datadir}/mime/packages/com.anthropic.Claude.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.anthropic.Claude.desktop
# Starting Electron needs a display, so only check the app is complete
test -x %{buildroot}%{appdir}/claude-desktop
test -f %{buildroot}%{appdir}/resources/app.asar

%files
%{_bindir}/claude-desktop
%{appdir}/
%{_datadir}/applications/com.anthropic.Claude.desktop
%{_datadir}/icons/hicolor/*/apps/claude-desktop.png
%{_datadir}/gnome-shell/search-providers/com.anthropic.Claude.search-provider.ini
%{_datadir}/dbus-1/services/com.anthropic.Claude.SearchProvider.service
%{_datadir}/mime/packages/com.anthropic.Claude.xml

%changelog
* Fri Nov 13 2026 oytal COPR <noreply@localhost> - 5.11492.2-1
- Initial COPR package
