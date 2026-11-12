# Go binary built in module mode; the COPR project needs "internet access
# during builds" (ENABLE_NET=on in package.env) to fetch Go modules.
%global debug_package %{nil}
%global goipath github.com/bjarneo/cliamp

Name:           cliamp
Version:        2.4.1
Release:        1%{?dist}
Summary:        Retro terminal music player inspired by Winamp 2.x

License:        MIT
URL:            https://%{goipath}
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  golang
BuildRequires:  gcc
BuildRequires:  git-core
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(flac)
BuildRequires:  pkgconfig(vorbis)
BuildRequires:  pkgconfig(ogg)
BuildRequires:  pkgconfig(libmpg123)
BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme
# AAC/ALAC/Opus/WMA playback and the YouTube/SoundCloud/etc. providers
Recommends:     /usr/bin/ffmpeg
Recommends:     yt-dlp
# Audio goes through ALSA; route it to PipeWire on a default Fedora desktop
Recommends:     pipewire-alsa

%description
cliamp is a terminal music player inspired by Winamp 2.x. It plays local
files, internet radio, podcasts and a range of streaming providers, with a
spectrum visualizer, playlists, lyrics and Lua plugins.

%prep
%autosetup -n %{name}-%{version}

%build
export GOPATH=%{_builddir}/go
export GOMODCACHE=%{_builddir}/go/pkg/mod
export GOFLAGS="-mod=mod -modcacherw"
export GOPROXY=https://proxy.golang.org,direct
# Lets go fetch a newer toolchain if upstream bumps go.mod past Fedora's golang
export GOTOOLCHAIN=auto
export CGO_ENABLED=1
export CGO_CFLAGS="%{build_cflags}"
export CGO_CPPFLAGS="%{build_cflags}"
export CGO_LDFLAGS="%{build_ldflags}"
go build -trimpath -buildmode=pie \
    -ldflags "-s -w -X main.version=v%{version} -linkmode=external -extldflags '%{build_ldflags}'" \
    -o %{name} .

%install
install -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 %{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
install -Dpm 0644 Cliamp.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
install -Dpm 0644 Cliamp.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
%{buildroot}%{_bindir}/%{name} --version

%files
%license LICENSE
%doc README.md config.toml.example
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%changelog
* Thu Nov 12 2026 github-actions <github-actions@users.noreply.github.com> - 2.4.1-1
- Update to 2.4.1

* Tue Nov 10 2026 cliamp COPR <noreply@localhost> - 2.4.0-1
- Initial COPR package
