# Support and help

MForce Enhanced Framework is an early-stage open-source project.
Community help is provided on a best-effort basis, with no guaranteed
response time or paid support agreement.

## Where to start

- [README and manual commands](README.md)
- [Termux/Linux contribution and setup guide](social/how_to_contribute.md)
- [OSINT documentation](docs/OSINT.md)
- [Offensive Security modules](docs/OFFENSIVE_XSS.md)
- [Update Center](README.md#update-mforce--update-center)
- [Privacy / DSGVO](DSGVO/README.md)
- [GitHub issues](https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/issues)

## Reporting a normal bug

Include your platform, relevant version, reproducible steps and
redacted output. Do not include real private targets or credentials.
Use the bug report issue template.

## Reporting a vulnerability

**Never post exploit details publicly.** Follow [SECURITY.md](SECURITY.md).

## Before asking for help

```bash
python3 -m unittest discover -s tests -v
bash src/functions/tcp401.sh --help
bash src/functions/upd501.sh --check
```

The updater requires an official Git clone on `main` with a clean
worktree; it will refuse unsupported setups. Test only systems you
own or are explicitly authorized to assess.
