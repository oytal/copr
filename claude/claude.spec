# The release is a single self-contained executable with its JavaScript payload
# appended to it: stripping or touching it would break it
%global debug_package %{nil}
%global __strip /bin/true
%global __brp_mangle_shebangs %{nil}

Name:           claude
Version:        2.1.331
Release:        1%{?dist}
Summary:        Claude Code, Anthropic's agentic coding tool for the terminal

# Proprietary, redistributed as published on the project's GitHub releases.
# Use is subject to https://www.anthropic.com/legal/commercial-terms
License:        LicenseRef-Anthropic-Commercial
URL:            https://github.com/anthropics/claude-code
# The "v" is TAG_PREFIX from package.env; change both together
# Both architectures are always sources: COPR downloads the sources once, for
# all chroots, so a source chosen with %ifarch is missing on the other arch
Source0:        %{url}/releases/download/v%{version}/claude-linux-x64.tar.gz
Source1:        %{url}/releases/download/v%{version}/claude-linux-arm64.tar.gz

ExclusiveArch:  x86_64 aarch64

Recommends:     git-core
Recommends:     ripgrep

%description
Claude Code is an agentic coding tool that lives in your terminal,
understands your codebase and helps you code faster by executing routine
tasks, explaining complex code and handling git workflows through natural
language commands.

This package repackages the official Linux release of Claude Code.

%prep
# The archive holds only the claude executable, not a directory
%setup -q -c -T
%ifarch aarch64
tar xzf %{SOURCE1}
%else
tar xzf %{SOURCE0}
%endif

%build
# Nothing to build: the release is a prebuilt executable

%install
install -Dpm 0755 claude %{buildroot}%{_bindir}/claude

%check
%{buildroot}%{_bindir}/claude --version

%files
%{_bindir}/claude

%changelog
* Tue Nov 24 2026 github-actions <github-actions@users.noreply.github.com> - 2.1.331-1
- Update to 2.1.331

* Sat Nov 21 2026 github-actions <github-actions@users.noreply.github.com> - 2.1.330-1
- Update to 2.1.330

* Fri Nov 20 2026 github-actions <github-actions@users.noreply.github.com> - 2.1.329-1
- Update to 2.1.329

* Thu Nov 19 2026 github-actions <github-actions@users.noreply.github.com> - 2.1.328-1
- Update to 2.1.328

* Wed Nov 18 2026 github-actions <github-actions@users.noreply.github.com> - 2.1.327-1
- Update to 2.1.327

* Tue Nov 17 2026 github-actions <github-actions@users.noreply.github.com> - 2.1.326-1
- Update to 2.1.326

* Mon Nov 16 2026 github-actions <github-actions@users.noreply.github.com> - 2.1.325-1
- Update to 2.1.325

* Mon Nov 16 2026 oytal COPR <noreply@localhost> - 2.1.323-2
- List both architectures' tarballs as sources: COPR downloads sources once
  for all chroots, so the aarch64 build had no tarball

* Fri Nov 13 2026 oytal COPR <noreply@localhost> - 2.1.323-1
- Initial COPR package
