# MForce — Guidelines and Terms of Use

> **Educational Purpose · Professional Usage · Authorized Targets Only**
>
> This file describes project usage expectations. It is not legal advice,
> an end-user contract signed by every downloader, a security certification,
> or a substitute for local law and the [MIT license](LICENSE).

## 1. What MForce is

MForce Enhanced Framework is a modular, open-source Bash/Python terminal
toolkit for Termux and Linux. It provides local system information, OSINT
checks, bounded network assessment utilities, an offline XSS example
library, an update mechanism and a static educational website.

The website's previews are illustrative. Terminal modules can perform
**real** network requests and must be used responsibly.

## 2. Permitted use

- Learn and practice in a controlled local laboratory.
- Inventory systems, domains, endpoints and services you own.
- Perform professional assessments with **prior explicit authorization**,
  a documented target scope, allowed methods and agreed time windows.
- Review public information when lawful and consistent with site policies.
- Contribute code, tests and documentation under the MIT license.

A public IP address or publicly accessible website is **not** automatic
permission to run an active assessment.

## 3. Prohibited misuse

Do not use the project for unauthorized access, harassment, service
disruption, credential theft, malware deployment, data exfiltration,
privacy invasion, evasion of access controls, or testing beyond your
authorization. Do not submit real XSS payloads to systems without
permission. Respect rate limits, robots guidance where relevant, and
the scope of any bug-bounty program.

## 4. Module-specific boundaries

| Module group | Behavior and limits |
| --- | --- |
| System information | Displays available local device/runtime details |
| OSINT | Performs public-information queries; some modes contact third-party services |
| TCP Port Scanner | Actual TCP connections; bounded ports, timeouts and workers |
| XSS Payload Lab | Offline reference payloads; no automatic requests or injection |
| HTTP Reflection Inspector | Actual bounded GET requests with harmless markers; reflection is not proof of XSS |
| Update Center | Fetches official GitHub `main` and fast-forwards only with a clean worktree |

Check the specific module's `--help` output and documentation before use.

## 5. Data protection and privacy

You are responsible for determining whether target URLs, IP addresses,
query parameters, domain registration details, logs or reports contain
personal data. Establish a lawful basis, minimize collection, set
retention limits, protect exports and assess international transfers
where applicable. Consult [DSGVO/](DSGVO/README.md) for an operational
checklist and **uncompleted legal templates**.

The repository does **not** claim universal GDPR/DSGVO compliance.
Website hosting and third-party endpoints may process connection
metadata; local shell history and manually exported reports may persist.

## 6. Vulnerability reports

Follow [SECURITY.md](SECURITY.md) for private reporting. Do not disclose
secrets, personal information or unpatched exploit details publicly.
The separate [Bug Bounty directory](Bug_Bounty/) contains program
information; a report does not guarantee a monetary reward.

## 7. Open-source license and warranty

Software is supplied under the [MIT license](LICENSE), including its
copyright, permission and warranty provisions. This document does not
change the license or impose new license conditions on the MIT-licensed
code. Third-party trademarks and services remain subject to their
respective terms.

## 8. Accuracy and limitations

Results are best-effort observations, not proof of a security weakness,
a legal compliance assessment or a penetration-testing certificate.
Network conditions, device permissions, DNS, proxy settings and remote
service behavior can change results. Back up important files before
updates or local modifications.

## 9. Community standards

Contributors and participants should follow
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md),
[CONTRIBUTING.md](CONTRIBUTING.md) and
[social/ai_usage.txt](social/ai_usage.txt).
The project can decline abusive contributions or unauthorized testing
requests without limiting rights under the MIT license.

## 10. Questions and updates

Use repository issues for non-sensitive questions. Security reports
must use a private channel as described in SECURITY.md. Policy changes
are tracked through Git history; this file does not assert acceptance
by every existing user.
