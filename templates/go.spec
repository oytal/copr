# Template for a Go application released on GitHub. Replace every TODO.
# Go fetches modules at build time: needs ENABLE_NET=on in package.env.
%global debug_package %{nil}
%global goipath github.com/TODO-owner/TODO-repo

Name:           TODO-name
Version:        TODO-version
Release:        1%{?dist}
Summary:        TODO one line, no trailing period

License:        TODO-SPDX
URL:            https://%{goipath}
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  golang
BuildRequires:  gcc
BuildRequires:  git-core
# TODO C libraries for cgo, as pkgconfig(...) where possible

%description
TODO a few sentences.

%prep
%autosetup -n TODO-repo-%{version}

%build
export GOPATH=%{_builddir}/go
export GOMODCACHE=%{_builddir}/go/pkg/mod
export GOFLAGS="-mod=mod -modcacherw"
export GOPROXY=https://proxy.golang.org,direct
export GOTOOLCHAIN=auto
export CGO_ENABLED=1
export CGO_CFLAGS="%{build_cflags}"
export CGO_LDFLAGS="%{build_ldflags}"
# TODO check upstream's Makefile/release workflow for the version ldflag and main package path
go build -trimpath -buildmode=pie \
    -ldflags "-s -w -X main.version=v%{version} -linkmode=external -extldflags '%{build_ldflags}'" \
    -o %{name} .

%install
install -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}

%check
# TODO a smoke test that works without a terminal or network
%{buildroot}%{_bindir}/%{name} --version

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%changelog
* TODO-date (e.g. Tue Nov 10 2026) oytal COPR <noreply@localhost> - TODO-version-1
- Initial COPR package
