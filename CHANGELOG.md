# Changelog

This project is in early development. The canonical application version is
defined in [cfg/zrk391.json](cfg/zrk391.json), currently **v0.01.2**.
Git history and merged pull requests provide the authoritative sequence of
changes; this file is a high-level summary, not a claim that a new release
tag has been published.

## Unreleased

- Shared dependency catalog for all external tools (Nmap, etc.)
- Automatic dependency installation and updates at tool manager startup
- Nmap integration under unified dependency management

## v0.01.2 (2026-11-23)

### Added
- Guided Nmap integration into the MForce Tool Manager (#75)
  - Arrow-driven scan profiles with fixed authorized-use scope
  - Single-target prompt with arrow-key confirmation
  - Bounded Nmap adapter with fixed scan profiles
  - Readiness check before showing scan profiles
- External Tool Manager overlay replacing legacy module menu (#74)
  - Arrow-key navigation for tool selection
  - External tool catalog with schema validation
  - Sourceable shell library components (`.lib` extension)
  - PTY-based terminal regression tests
- Automatic Nmap package installation and updates
- Repository statistic badges (auto-refreshed)

### Fixed
- Shell variable expansion in Nmap adapter and UI
- Control-character validation for tool descriptions
- Hostname validation regex interpolation
- Terminal escape sequences in PTY tests
- Startup keyboard regression for registered Nmap tool

## v0.01.2-3 (2026-10-28)

### Fixed
- Post-contribution validation gaps (#69)
- Dependency updates: docker/setup-buildx-action 3→4, actions/github-script 7→9 (#71, #72)

### Added
- Contributor recognition directory (`!CONTRIBUTORS/`) (#67)
- Community governance documents (DSGVO, AI usage policy, Code of Conduct)

## v0.01.2-2 (2026-10-18)

### Added
- Rahul-pamula recognized as first external contributor with 5 accepted PRs (#64–#68)
  - Category registry schema checks and invalid-input fixtures (#64)
  - Category-reference checks and orphaned-module fixtures (#65)
  - Shell syntax checks for public module entry points (#66)
  - Filesystem and Git-index executable-permission checks (#67)
  - Tests for protective attributes on links opening new tabs (#68)
- Offline schema validation for Shields statistics JSON (#55)
- External link safety verification (rel attributes for target=_blank) (#53)
- Executable file permission and git mode verification on shell entry points (#37)
- Shell syntax checks for public module entry points (#34)
- Registry category reference verification with orphaned module fixtures (#48)
- Offline schema checks for category registry (#47)

### Fixed
- Validation gaps after contributor merges

## v0.01.2 (2026-10-16)

### Added
- Contributor credits and recognition principles documentation
- MIT License copyright attribution update

## 2026-10-15 — Big Update Phase 1 (#62)

### Added
- Modular plugin architecture (net, osint, offensive, defensive, file, cfg, util, sys, upd)
- Doctor CLI for system diagnostics
- 500/150 roadmap documentation
- Website refresh with enterprise design
- Independent Academy course overview

## 2026-10-14

### Added
- Publish Linux CLI as GitHub Packages OCI image on main pushes (#28)
- Build and publish ready-to-install MForce ZIP/tar.gz packages automatically (#27)
- Automatic repository statistic badges (code lines, files, directories) (#25)
- jq and platform architecture badges in README (#22)

## 2026-10-13

### Fixed
- Website paths and design improvements (#6)
- CI privacy and release hardening (#23, #24)

## 2026-10-12

### Added
- MariaDB logging documentation (#21)

## 2026-10-11

### Added
- CLI installable package feature (#20)

## 2026-10-10

### Added
- MForce AI Security Bot framework scan report (#19)

## 2026-10-09

### Added
- Security scanner canary tests (#17, #18)
- Defense in depth bots (#17)

## 2026-10-08

### Added
- Dependabot GitHub Actions updates (#16)

## 2026-10-07

### Added
- Community governance DSGVO documentation (#15)

## 2026-10-06

### Added
- XSS Payload Lab and HTTP Reflection Inspector (#14)
- Glass-motion website v7 with Academy tutorials (#13)
- Terminal updater with interactive progress (#11)
- Authorized TCP Port Scanner (#10)
- OSINT suite with web audit and responsible use (#9)
- Enterprise terminal workspace (#8)
- Interactive site with motion design for Linux (#7)

## Existing framework capabilities (current `main`)

- Bash terminal interface for Termux and Linux, startup confirmation and modular registry
- Local system/network information and ten OSINT inspection modes
- Authorized TCP Connect Port Scanner
- Offline XSS Payload Lab and bounded HTTP Reflection Inspector
- Git fast-forward Update Center with interactive progress
- Static glass-style website with interactive tutorials and an Academy roadmap (courses and certificates not yet offered)
- Python regression suite and GitHub Actions workflow

---

Do not infer a release date or production-readiness guarantee from the
presence of these features. Refer to GitHub commits and PRs for details.