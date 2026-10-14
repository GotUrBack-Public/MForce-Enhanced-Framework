# MForce installable packages

MForce is automatically packaged from the current `main` branch on every
push. The workflow runs the full regression suite and ShellCheck, then
publishes both **ZIP** and **tar.gz** archives with `SHA256SUMS` to a public
GitHub Release. Packages include the application, all enabled tools, docs,
tests and an **offline installer**. No clone or GitHub account is required
to install a downloaded package.

Latest published release:
https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/releases/latest

## Linux / Termux

1. Download either archive from the latest release.
2. Extract the archive.
3. Run the installer from the extracted directory:

```bash
bash mforce-enhanced-framework/packaging/install-local.sh
~/.local/bin/mforce
```

The installer copies the complete package to
`~/.local/share/mforce-enhanced-framework` and creates
`~/.local/bin/mforce`. It **never overwrites an existing installation**.
Set `MFORCE_INSTALL_DIR` and `MFORCE_BIN_DIR` to choose alternate paths.

The package includes the application but does not install OS dependencies.
Install `bash`, `jq`, `python3` and platform-specific utilities as
needed. Git is **not** required for this offline installation.

## Verify archive integrity

Download `SHA256SUMS` alongside the two archives, then run:

```bash
sha256sum -c SHA256SUMS
```

Checksums detect accidental corruption; for high-assurance supply-chain
verification also verify the GitHub workflow, source commit and publisher.
The release name includes the source commit prefix.

The existing Git-clone installer (`install.sh`) remains available and
unchanged.
