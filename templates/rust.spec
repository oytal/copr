# Template for a Rust application released on GitHub. Replace every TODO.
# Cargo fetches crates at build time: needs ENABLE_NET=on in package.env.
%global debug_package %{nil}

Name:           TODO-name
Version:        TODO-version
Release:        1%{?dist}
Summary:        TODO one line, no trailing period

License:        TODO-SPDX
URL:            https://github.com/TODO-owner/TODO-repo
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
# TODO C libraries for -sys crates, as pkgconfig(...) where possible

%description
TODO a few sentences.

%prep
%autosetup -n TODO-repo-%{version}

%build
export CARGO_HOME=%{_builddir}/cargo
export RUSTFLAGS="%{build_rustflags}"
# Drop --locked if upstream does not commit Cargo.lock
cargo build --release --locked

%install
# TODO binary name may differ from the package name; check [[bin]] in Cargo.toml
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

%check
# TODO a smoke test that works without a terminal or network
%{buildroot}%{_bindir}/%{name} --version

%files
%license LICENSE*
%doc README.md
%{_bindir}/%{name}

%changelog
* TODO-date (e.g. Tue Nov 10 2026) oytal COPR <noreply@localhost> - TODO-version-1
- Initial COPR package
