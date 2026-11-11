# Rust binary; Cargo fetches crates at build time, so the COPR project needs
# "internet access during builds" (ENABLE_NET=on in package.env).
%global debug_package %{nil}

Name:           kubie
Version:        0.28.0
Release:        1%{?dist}
Summary:        More powerful alternative to kubectx and kubens

License:        Zlib
URL:            https://github.com/kubie-org/kubie
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc

# kubie runs kubectl for namespaces and inside its context shells
Recommends:     /usr/bin/kubectl

%description
kubie is an alternative to kubectx, kubens and the k on prompt modification
script. It offers context switching, namespace switching and prompt
modification in a way that makes each shell independent from others. It
also supports split configuration files, so it can load Kubernetes contexts
from multiple files.

%prep
%autosetup -n %{name}-%{version}

%build
export CARGO_HOME=%{_builddir}/cargo
# Fedora sets -Cstrip=none (for debuginfo); strip here since debuginfo is off
export RUSTFLAGS="%{build_rustflags} -Cstrip=symbols"
# No "update" feature: the self-updater has no place in an RPM-managed binary
cargo build --release --locked --no-default-features

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
# Upstream's hand-written bash/fish completions also complete context and
# namespace names; zsh gets the clap-generated one
install -Dpm 0644 completion/%{name}.bash %{buildroot}%{bash_completions_dir}/%{name}
install -Dpm 0644 completion/%{name}.fish %{buildroot}%{fish_completions_dir}/%{name}.fish
install -d %{buildroot}%{zsh_completions_dir}
target/release/%{name} generate-completion zsh > %{buildroot}%{zsh_completions_dir}/_%{name}

%check
%{buildroot}%{_bindir}/%{name} --version

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}
%{fish_completions_dir}/%{name}.fish
%{zsh_completions_dir}/_%{name}

%changelog
* Wed Nov 11 2026 oytal COPR <noreply@localhost> - 0.28.0-1
- Initial COPR package
