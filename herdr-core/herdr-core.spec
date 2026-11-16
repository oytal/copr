# Rust binary linking libghostty-vt, which build.rs compiles with Zig from the
# vendor/ghostty git submodule. Cargo, Zig and %%prep (the submodule) download
# at build time, so the COPR project needs ENABLE_NET=on in package.env.
%global debug_package %{nil}

Name:           herdr-core
Version:        0.1.21
Release:        1%{?dist}
Summary:        Terminals for coding agents (hc), the core of the Herdr app

# herdr-core is Apache-2.0; the libghostty-vt it links is MIT
License:        Apache-2.0 AND MIT
URL:            https://github.com/herdrdev/herdr-core
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  zig >= 0.16
# %%prep fetches the vendor/ghostty submodule
BuildRequires:  git-core
BuildRequires:  curl
BuildRequires:  tar

%description
herdr-core (hc) runs terminals for coding agents in a background server:
start, read, wait on and talk to terminals from scripts and agents, and keep
them running while the frontend that shows them comes and goes. It is the
core the Herdr desktop app (herdr-app) runs on.

%prep
%autosetup -n %{name}-%{version}
# vendor/ghostty is a git submodule, which GitHub tarballs leave out.
# Read the commit this tag pins and fetch that Ghostty source.
git clone -q --bare --depth 1 --filter=blob:none --branch v%{version} %{url}.git %{_builddir}/%{name}-gitlink
ghostty=$(git -C %{_builddir}/%{name}-gitlink rev-parse HEAD:vendor/ghostty)
rm -rf %{_builddir}/%{name}-gitlink
mkdir -p vendor/ghostty
curl -fsSL --retry 3 https://github.com/ghostty-org/ghostty/archive/$ghostty.tar.gz |
  tar -xz --strip-components=1 -C vendor/ghostty

%build
export CARGO_HOME=%{_builddir}/cargo
export ZIG_GLOBAL_CACHE_DIR=%{_builddir}/zig-cache
# Fedora sets -Cstrip=none (for debuginfo); strip here since debuginfo is off
export RUSTFLAGS="%{build_rustflags} -Cstrip=symbols"
cargo build --release --locked -p herdr-core

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
# Upstream's docs call it hc; its installer adds hc next to herdr-core
ln -s %{name} %{buildroot}%{_bindir}/hc

%check
%{buildroot}%{_bindir}/%{name} --version | grep -q '^hc '

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{_bindir}/hc

%changelog
* Thu Nov 12 2026 github-actions <github-actions@users.noreply.github.com> - 0.1.21-1
- Update to 0.1.21

* Wed Nov 11 2026 oytal COPR <noreply@localhost> - 0.1.20-1
- Initial COPR package
