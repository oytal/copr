# Argo CD CLI, a Go binary linked against glibc (cgo). The COPR project needs
# network during builds (ENABLE_NET=on) to fetch Go modules, and f44 ships
# Go 1.26 while go.mod wants 1.27, so GOTOOLCHAIN=auto downloads a newer
# toolchain.
%global debug_package %{nil}
%global verpkg     github.com/argoproj/argo-cd/v3/common

Name:           argocd
Version:        3.6.1
Release:        1%{?dist}
Summary:        Declarative GitOps for Kubernetes, CLI client

License:        Apache-2.0
URL:            https://github.com/argoproj/argo-cd
# The "v" is TAG_PREFIX from package.env; change both together. The archive
# keeps the repo name argo-cd even though the package is named argocd.
Source0:        %{url}/archive/refs/tags/v%{version}/argo-cd-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  golang
BuildRequires:  gcc
BuildRequires:  git-core

%description
Argo CD is a declarative, GitOps continuous delivery tool for Kubernetes.
The argocd CLI talks to the Argo CD API server and handles login, app
management, syncs, and the admin and troubleshooting commands.

%prep
%autosetup -n argo-cd-%{version}

%build
export GOPATH=%{_builddir}/go
export GOMODCACHE=%{_builddir}/go/pkg/mod
export GOFLAGS="-mod=mod -modcacherw"
export GOPROXY=https://proxy.golang.org,direct
# Allows go to fetch a newer toolchain than Fedora's golang when go.mod asks
export GOTOOLCHAIN=auto
export CGO_ENABLED=1
export CGO_CFLAGS="%{build_cflags}"
export CGO_LDFLAGS="%{build_ldflags}"
go build -trimpath -buildmode=pie \
    -ldflags "-s -w -X %{verpkg}.version=%{version} -linkmode=external -extldflags '%{build_ldflags}'" \
    -o %{name} ./cmd

%install
install -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}

%check
%{buildroot}%{_bindir}/%{name} version --client

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%changelog
* Fri Nov 13 2026 oytal COPR <noreply@localhost> - 3.6.1-1
- Initial COPR package