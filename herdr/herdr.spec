# Rust binary with a vendored libghostty-vt that build.rs compiles with Zig.
# Cargo and Zig fetch dependencies at build time, so the COPR project needs
# "internet access during builds" (ENABLE_NET=on in package.env).
%global debug_package %{nil}

Name:           herdr
Version:        0.9.5
Release:        1%{?dist}
Summary:        Terminal workspace manager for AI coding agents

# herdr is Apache-2.0; vendored libghostty-vt and portable-pty are MIT
License:        Apache-2.0 AND MIT
URL:            https://github.com/herdrdev/herdr
# The "v" is TAG_PREFIX from package.env; change both together
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  x86_64 aarch64

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
# libghostty-vt's build.rs runs `zig build` (upstream needs Zig 0.16)
BuildRequires:  zig >= 0.16

%description
herdr is the runtime coding agents live on: a terminal multiplexer (TUI)
with workspaces, tabs and panes that detects the agents running in them,
shows their state, and lets agents drive each other through a CLI and
socket API.

The desktop app and its terminal core are packaged as herdr-app and
herdr-core.

%prep
%autosetup -n %{name}-%{version}

%build
export CARGO_HOME=%{_builddir}/cargo
export ZIG_GLOBAL_CACHE_DIR=%{_builddir}/zig-cache
# Fedora sets -Cstrip=none (for debuginfo); strip here since debuginfo is off
export RUSTFLAGS="%{build_rustflags} -Cstrip=symbols"
cargo build --release --locked -p herdr

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -d %{buildroot}%{bash_completions_dir} %{buildroot}%{zsh_completions_dir} %{buildroot}%{fish_completions_dir}
target/release/%{name} completion bash > %{buildroot}%{bash_completions_dir}/%{name}
target/release/%{name} completion zsh > %{buildroot}%{zsh_completions_dir}/_%{name}
target/release/%{name} completion fish > %{buildroot}%{fish_completions_dir}/%{name}.fish

%check
%{buildroot}%{_bindir}/%{name} --version

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}
%{zsh_completions_dir}/_%{name}
%{fish_completions_dir}/%{name}.fish

%changelog
* Wed Nov 11 2026 oytal COPR <noreply@localhost> - 0.9.5-1
- Initial COPR package
