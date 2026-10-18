# How to contribute to MForce

Thanks for improving MForce Enhanced Framework. The project targets **Termux
and Linux**, combines a Bash terminal interface with Python 3 security
utilities, and uses static HTML/CSS/JavaScript for its website.

## Before you start

1. Read [README.md](../README.md), [SECURITY.md](../SECURITY.md),
   [Code of Conduct](../CODE_OF_CONDUCT.md), and
   [AI usage](ai_usage.txt).
2. Check [open issues](https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/issues)
   and [pull requests](https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/pulls)
   to avoid duplicate work.
3. For major architecture changes, new offensive modules or changes to the
   project's data handling, open an issue to discuss scope first.
4. Never put credentials, private target information, personal data or
   unreleased vulnerability details in a public issue or PR.

## Development setup

Clone your fork, install the runtime dependencies, and start a feature branch:

```bash
git clone https://github.com/YOUR-USERNAME/MForce-Enhanced-Framework.git
cd MForce-Enhanced-Framework
git remote add upstream https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git
git checkout -b fix/short-description
```

Termux prerequisites:

```bash
pkg update
pkg install git bash jq python coreutils ncurses-utils iproute2
```

Debian / Ubuntu prerequisites:

```bash
sudo apt update
sudo apt install git bash jq python3 coreutils ncurses-bin iproute2
```

Run MForce and its tests:

```bash
bash xrm742.sh
python3 -m unittest discover -s tests -v
```

Optional checks where installed:

```bash
git diff --check
for script in src/functions/*.sh xrm742.sh install.sh; do
    bash -n "$script" || exit 1
done
find src -name '*.sh' -exec bash -c '
    for script do bash -n "$script" || exit 1; done
' _ {} +
node --check web/js/main.js
```

## Project layout

| Path | Purpose |
| --- | --- |
| `src/functions/` | Public shell entry points |
| `src/lib/<id>/` | Module implementation and `.json`, `.conf`, `.help` metadata |
| `src/data/` | Function and category registries |
| `src/osint/`, `src/offensive/` | Python modules |
| `src/ui/`, `src/core/` | Terminal UI and runtime |
| `src/update/` | Update Center |
| `web/` | Static website and interactive tutorials |
| `tests/` | Regression tests |
| `DSGVO/` | Privacy governance templates and data-flow documentation |

## Adding a module

1. Propose a narrowly scoped function and its authorization requirements.
2. Choose a unique module ID; avoid collisions with existing IDs.
3. Add `src/functions/<id>.sh` and `src/lib/<id>/` with a shell entry
   point, metadata JSON, configuration and meaningful help text.
4. Register the module in `src/data/funcs.json`; use an existing category
   from `src/data/cats.json` or document a new one.
5. Keep shell entry points executable (`chmod +x`).
6. Validate input, network scope, timeouts and bounded output; refuse
   dangerous defaults. No unauthorized scans, evasion, exfiltration,
   credential theft or destructive actions.
7. Add automated tests, document limitations and provide real commands in
   the README's **Manuell / Manual Commands** section.

Avoid making up success results or vulnerability findings. Reflection,
header presence and suspicious JavaScript patterns are not confirmed exploits.

## Website contributions

Use semantic HTML, accessible labels, keyboard navigation, sufficient
contrast, responsive layouts and `prefers-reduced-motion`. Keep the website
static; it must not secretly execute security scans. Prefer local assets,
avoid third-party trackers and explain any new external requests. Run the
website tests and manually check mobile and desktop layouts.

## Pull-request checklist

- [ ] The change has a focused purpose and links a relevant issue (if any).
- [ ] I reviewed my diff and documented behavior, limitations and usage.
- [ ] New functionality has relevant tests; I ran the tests I claim.
- [ ] Bash syntax, JSON schemas, module registration and permissions are valid.
- [ ] I tested Termux or Linux where possible and stated untested platforms.
- [ ] No secrets, personal data or sensitive target information are included.
- [ ] Security-relevant actions require appropriate authorization.
- [ ] I disclosed material AI assistance and verified generated output.
- [ ] I checked licenses, attribution, privacy and documentation links.

Submit your branch as a pull request against `main`. Maintainers may request
changes or decline proposals that do not fit the project's scope. Do not
force-push someone else's branch without consent.

## Bug reports and vulnerability disclosures

Use the [bug report template](../.github/ISSUE_TEMPLATE/bug_report.md) for
ordinary reproducible bugs. For a security vulnerability, **do not open a
public issue with exploit details**; follow [SECURITY.md](../SECURITY.md).

## Documentation and translations

Keep code samples copyable and executable. Label sample outputs clearly;
never present illustrative website data as live scan results. Explain the
difference between local processing and external network requests. German
and English improvements are welcome; keep terms consistent across files.

## Licensing

By submitting a contribution, you agree to provide it under the
repository's [MIT license](../LICENSE) and confirm that you have the rights
needed to contribute it. Preserve third-party attribution.
