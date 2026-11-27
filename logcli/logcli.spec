# Only logcli is built from the Loki source tree (make logcli).
# Loki ships a vendor/ directory, so the build needs no network.
%global debug_package %{nil}

Name:           logcli
Version:        3.7.11
Release:        1%{?dist}
Summary:        Command-line client for Grafana Loki

License:        AGPL-3.0-only
URL:            https://github.com/grafana/loki
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/loki-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  golang >= 1.26.10

%description
logcli is the command-line interface to Grafana Loki. It runs LogQL queries
against a Loki server, tails logs, lists labels and series, and queries
index statistics and volume.

%prep
%autosetup -n loki-%{version}

%build
export GOFLAGS="-mod=vendor"
export GOTOOLCHAIN=local
export CGO_ENABLED=0
# Same version variables as upstream's Makefile (GO_LDFLAGS)
VPREFIX=github.com/grafana/loki/v3/pkg/util/build
go build -trimpath -tags netgo \
    -ldflags "-s -w -X ${VPREFIX}.Version=%{version} -X ${VPREFIX}.Branch=release -X ${VPREFIX}.BuildUser=copr" \
    -o %{name} ./cmd/logcli

%install
install -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}
# Upstream documents "eval $(logcli --completion-script-bash|zsh)"; ship the
# same scripts as files so the shells load them by themselves
install -d %{buildroot}%{bash_completions_dir} %{buildroot}%{zsh_completions_dir}
./%{name} --completion-script-bash > %{buildroot}%{bash_completions_dir}/%{name}
./%{name} --completion-script-zsh > %{buildroot}%{zsh_completions_dir}/_%{name}

%check
%{buildroot}%{_bindir}/%{name} --version

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}
%{zsh_completions_dir}/_%{name}

%changelog
* Fri Nov 27 2026 github-actions <github-actions@users.noreply.github.com> - 3.7.11-1
- Update to 3.7.11

* Wed Nov 18 2026 oytal COPR <noreply@localhost> - 3.7.10-1
- Initial COPR package
