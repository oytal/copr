%global debug_package %{nil}

Name:           starship
Version:        1.27.0
Release:        1%{?dist}
Summary:        Minimal, fast and customizable prompt for any shell

License:        ISC
URL:            https://github.com/starship/starship
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust >= 1.95
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc

%description
Starship is a cross-shell prompt written in Rust. It shows only the
information that is relevant to what you are doing, such as the git branch,
the language version of the current project or the duration of the last
command. It works with bash, zsh, fish, nushell, PowerShell and others.

%prep
%autosetup -n %{name}-%{version}

%build
export CARGO_HOME=%{_builddir}/cargo
# Fedora sets -Cstrip=none (for debuginfo); strip here since debuginfo is off
export RUSTFLAGS="%{build_rustflags} -Cstrip=symbols"
cargo build --release --locked

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

# Shell completions, in the locations each shell's package looks in
install -d %{buildroot}%{_datadir}/bash-completion/completions
%{buildroot}%{_bindir}/%{name} completions bash > %{buildroot}%{_datadir}/bash-completion/completions/%{name}
install -d %{buildroot}%{_datadir}/zsh/site-functions
%{buildroot}%{_bindir}/%{name} completions zsh > %{buildroot}%{_datadir}/zsh/site-functions/_%{name}
install -d %{buildroot}%{_datadir}/fish/vendor_completions.d
%{buildroot}%{_bindir}/%{name} completions fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/%{name}.fish

%check
%{buildroot}%{_bindir}/%{name} --version
%{buildroot}%{_bindir}/%{name} module character >/dev/null

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/bash-completion/completions/%{name}
%{_datadir}/zsh/site-functions/_%{name}
%{_datadir}/fish/vendor_completions.d/%{name}.fish

%changelog
* Fri Nov 13 2026 oytal COPR <noreply@localhost> - 1.27.0-1
- Initial COPR package
