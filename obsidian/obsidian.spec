# Prebuilt Electron app repackaged from upstream's release tarballs: no
# debuginfo, no stripping
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs %{nil}
# Libraries shipped inside the app directory are not system provides
%global __provides_exclude_from ^%{_libdir}/obsidian/.*$
%global __requires_exclude ^(libffmpeg|libEGL|libGLESv2|libvk_swiftshader|libvulkan)\\.so.*$

Name:           obsidian
Version:        1.15.1
Release:        1%{?dist}
Summary:        Knowledge base that works on top of a folder of Markdown files

# Obsidian is proprietary, free for personal and commercial use. The license
# terms are at https://obsidian.md/license
License:        LicenseRef-Proprietary
URL:            https://obsidian.md
# The "v" is TAG_PREFIX from package.env; change both together
%ifarch aarch64
Source0:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian-%{version}-arm64.tar.gz
%else
Source0:        https://github.com/obsidianmd/obsidian-releases/releases/download/v%{version}/obsidian-%{version}.tar.gz
%endif
Source1:        md.obsidian.Obsidian.desktop
Source2:        obsidian.xml

ExclusiveArch:  x86_64 aarch64

BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme
Requires:       xdg-utils
Recommends:     libappindicator-gtk3
Recommends:     libsecret

%description
Obsidian is a note-taking and knowledge base application that works on top of
a local folder of plain text Markdown files. It supports links between notes,
a graph view, canvases, community plugins and themes.

This package repackages the official Linux release of Obsidian.

%prep
%setup -q -n obsidian-%{version}

%build
# Nothing to build: the release is a prebuilt Electron application

%install
install -d %{buildroot}%{_libdir}/obsidian
cp -a . %{buildroot}%{_libdir}/obsidian/
install -d %{buildroot}%{_bindir}
ln -s %{_libdir}/obsidian/obsidian %{buildroot}%{_bindir}/obsidian

install -Dpm 0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/md.obsidian.Obsidian.desktop
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/mime/packages/obsidian.xml
install -Dpm 0644 resources/icon.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/obsidian.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/md.obsidian.Obsidian.desktop
# Starting Electron needs a display, so only check the app is complete
test -x %{buildroot}%{_libdir}/obsidian/obsidian
test -f %{buildroot}%{_libdir}/obsidian/resources/app.asar

%files
%{_bindir}/obsidian
%{_libdir}/obsidian/
%{_datadir}/applications/md.obsidian.Obsidian.desktop
%{_datadir}/mime/packages/obsidian.xml
%{_datadir}/icons/hicolor/512x512/apps/obsidian.png

%changelog
* Fri Nov 13 2026 oytal COPR <noreply@localhost> - 1.15.1-1
- Initial COPR package
