# MForce on GitHub Packages (GHCR)

The MForce Linux CLI is automatically built and published as a multi-platform
OCI container package to GitHub Container Registry (GHCR) after every push to
`main`. This is **separate** from the downloadable ZIP/tar.gz releases.

Package: `ghcr.io/goturback-public/mforce-enhanced-framework`

Package page (visible after first successful workflow):
https://github.com/orgs/GotUrBack-Public/packages/container/package/mforce-enhanced-framework

Run on Linux with Docker:

```bash
docker pull ghcr.io/goturback-public/mforce-enhanced-framework:latest
docker run --rm -it --network none ghcr.io/goturback-public/mforce-enhanced-framework:latest
```

For authorized network checks, replace `--network none` with a network
configuration suitable for the permitted target; the container defaults to
Docker's network settings if no network option is specified. Do not grant
privileged mode or host network access unless explicitly required and approved.

The container uses Debian Bookworm, supports amd64 and arm64, runs as an
unprivileged user and starts the existing CLI through Bash. No change to
Termux-specific launch scripts is necessary. A terminal is needed for the
interactive UI (`-it`). Local data does not persist unless you mount a volume.

The GitHub Actions workflow requires the repository's `GITHUB_TOKEN` to have
`packages: write` access. Repository/org package policies may prevent
publishing; inspect the workflow logs if publication fails. A package's
visibility (public/private) is governed by GHCR package settings, independently
of repository visibility.

For native Termux installations, use the release archives instead:
https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/releases/latest
