# MForce Enhanced Framework — Windows 11 / PowerShell 7

Dedicated development branch: platform/windows11-powershell

This is a native PowerShell front end for the same MForce module registry used
by Termux/Linux. It runs directly in Windows Terminal without Bash, WSL,
Termux or an elevated Administrator session.

## Requirements

- Windows 11 and PowerShell 7+ (pwsh).
- Python 3.10+ on PATH for the existing shared inspection/audit engines.
- Git for Windows is optional and used only for update/status actions.

Install PowerShell 7 and Python from their official installers. Do not change
machine-wide execution policy or execute remote bootstrap scripts.

## Start

In a checkout of this branch, open PowerShell 7 in the repository folder:

    pwsh -NoProfile -File .\windows\MForce.ps1

Commands for automation:

    pwsh -NoProfile -File .\windows\MForce.ps1 -List
    pwsh -NoProfile -File .\windows\MForce.ps1 -Doctor
    pwsh -NoProfile -File .\windows\MForce.ps1 -Module sys193
    pwsh -NoProfile -File .\windows\MForce.ps1 -Module frc386
    pwsh -NoProfile -File .\windows\MForce.ps1 -Module dns211 -Target example.org
    pwsh -NoProfile -File .\windows\MForce.ps1 -Module web311 -Target https://example.org
    pwsh -NoProfile -File .\windows\MForce.ps1 -Module sec601 -Target .\my-project

For explicitly authorized active checks only:

    pwsh -NoProfile -File .\windows\MForce.ps1 -Module tcp401 -Target 127.0.0.1 -Authorized
    pwsh -NoProfile -File .\windows\MForce.ps1 -Module cor404 -Target https://your-authorized-domain.example -Authorized -AllowPublic

Additional engine options can be passed using -ModuleArgs:

    pwsh -NoProfile -File .\windows\MForce.ps1 -Module xss402 -ModuleArgs '--list-categories'

For update status (no changes):

    pwsh -NoProfile -File .\windows\MForce.ps1 -Module upd501

To explicitly fast-forward the Git checkout:

    pwsh -NoProfile -File .\windows\MForce.ps1 -Module upd501 -ModuleArgs '--apply'

## Architecture and parity

The PowerShell launcher reads the same src/data/funcs.json and
src/data/cats.json as the existing framework. All 21 enabled modules are
mapped; the 2 disabled modules remain disabled. The Windows UI offers
categories, module selection, target prompts and authorization prompts.

- Native Windows PowerShell cmdlets: network inventory (frc386), system
  inventory (sys193) and Git update/status (upd501).
- Shared cross-platform Python engines: DNS, IP, TLS, HTTP headers, website
  inspection, API metadata, rate-limit evidence, JavaScript/DOM review,
  robots/sitemap, RDAP, TCP checks, reflection inspection, CORS/method/cookie/
  path audits, offline XSS lab and local secret pattern review.

The Bash-specific UI, Linux-specific environment data, shell module wrappers
and optional Linux database service are not ported or invoked. This is
functional module parity through PowerShell orchestration, not a byte-for-byte
rewrite of every Python engine into PowerShell. Outputs can differ because of
Windows networking and OS APIs.

Active network modules require -Authorized; public targets additionally
require -AllowPublic and are validated inside the shared Python engine.
Passive OSINT requests are bounded and public-target-only. Never scan a
system without explicit authorization. Local secret audit is offline.

## Test

On Windows 11 with PowerShell 7 and Python:

    pwsh -NoProfile -File .\windows\tests\Windows.Tests.ps1
    python -m unittest tests.test_windows_port -v

CI also runs these checks on GitHub windows-latest runners whenever this
branch is updated. This branch is deliberately not merged into main.
