# Security policy — MForce Enhanced Framework

MForce is an early-stage Termux/Linux security toolkit. This policy covers
vulnerabilities **in the MForce source code and its official website**.
It does not authorize assessments of third-party infrastructure.

## Supported versions

Security fixes target the current `main` branch. Older branches, clones,
forks and snapshots are **not guaranteed** to receive security updates.
The current application version is defined in
[cfg/zrk391.json](cfg/zrk391.json); no formal long-term-support schedule
is offered.

## Reporting a vulnerability

**Do not publish unpatched exploit details, private targets, credentials,
personal data or sensitive device logs in a public GitHub issue.**

1. Check whether GitHub **Private Vulnerability Reporting** is available
   under the repository's Security tab and use it if enabled.
2. If private reporting is unavailable, open a **minimal public issue**
   asking the maintainers to provide a private contact method. Do not
   include a proof of concept, exploit chain or sensitive details.
3. Once a private channel is agreed, share the affected component and
   version, impact, safe reproduction steps, expected vs actual behavior
   and suggested mitigation. Use redacted or synthetic data.
4. Allow time for investigation and coordinated disclosure.

There is currently **no published dedicated security inbox**, fixed
response SLA, guaranteed embargo duration or guaranteed bounty payout.
Do not assume a public issue is confidential.

## Trust and authorization boundaries

- The startup code is a **visible interaction confirmation**, not
  authentication or a security boundary. Shell modules can be run directly.
- Session JSON stores local run metadata, not an access token. Temporary
  session files use restricted permissions and are removed on normal exit
  or handled signals; forced termination can leave remnants.
- The toolkit does not require root. Run trusted code as a regular user.
- Local MariaDB audit logging is **disabled by default**. Opt in with
  `MF_DB_ENABLE=1`; only module ID, exit status and timestamp are stored.
  Raw module output is not captured. The default seven-day retention is
  enforced on the next database-enabled start, not by a background timer.
  Legacy raw output is cleared on that start; review local backups separately.
- OSINT modules make real public-information network requests; RDAP
  forwards target details to `rdap.org`.
- The TCP scanner makes real, bounded connections. The reflection
  inspector makes bounded GET requests with harmless markers.
- XSS Payload Lab is an **offline** library. Example payloads can
  execute when deliberately placed into a vulnerable lab context.
- The Update Center checks the official Git remote, clean worktree and
  fast-forward history. It is not a cryptographic attestation of
  individual commits or a guarantee against a compromised upstream.
- Network-scope checks, DNS resolution and authorization flags do not
  replace written permission. DNS changes between validation and
  connection remain a possible risk.

## Research rules

Test only software or environments you own or are explicitly authorized
to assess. Avoid destructive testing, third-party scans, exfiltration,
denial of service, social engineering and public disclosure of
unpatched findings. Keep traffic low and stop when unexpected
operational impact is observed.

For the separate bounty-program description, see
[Bug_Bounty/Our_Programm](Bug_Bounty/Our_Programm). Rewards are
discretionary and must not be assumed from this security policy.

## Security and privacy documentation

- [Guidelines and Terms of Use](GUIDLINES&&TERMSOFUSE.md)
- [DSGVO / GDPR documentation](DSGVO/README.md)
- [Data-flow inventory](DSGVO/DATENFLUESSE.md)
- [Incident response template](DSGVO/INCIDENT_RESPONSE.md)

## Maintainer response

Maintainers may triage a report, request clarification, reproduce the
issue, prepare a fix, run regression tests and coordinate disclosure.
The absence of an immediate response is not an authorization to
test unrelated systems or disclose sensitive data.
