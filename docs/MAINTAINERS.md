# Maintainer handbook

This guide describes a recommended review and release workflow for
MForce. It is not a claim that the project has a formal release
committee, SLA or compliance certification.

## Triage

- Bugs: request a minimal, redacted reproduction and platform details.
- Features: confirm scope, compatibility, dependencies and acceptance tests.
- Security: move to private disclosure as described in [SECURITY.md](../SECURITY.md).
- Privacy: review [DSGVO/DATENFLUESSE.md](../DSGVO/DATENFLUESSE.md)
  and the [checklist](../DSGVO/CHECKLISTE.md).
- Conduct: avoid exposing personal information in public discussions.

## Review requirements

1. Review the actual diff and check that no secrets or personal data were
   introduced.
2. Verify executable shell entry points, unique JSON module IDs,
   configuration metadata and help text.
3. Run `python3 -m unittest discover -s tests -v` and review CI.
4. For web changes, verify keyboard navigation, reduced-motion behavior,
   mobile layout and third-party requests.
5. For security modules, check target authorization, request limits,
   redirects, DNS resolution, timeout handling and honest findings.
6. Confirm README/manual commands, docs and CHANGELOG are accurate.
7. Check license and attribution; verify any AI-generated content.

## Suggested release procedure

- Review and merge tested changes to `main`.
- Decide whether the changes warrant a new version.
- Update `cfg/zrk391.json`, README badge and `CHANGELOG.md`
  **together**; avoid version drift.
- Run CI on the final commit and, where possible, a physical Termux test.
- Verify the published GitHub Pages website after deployment.
- Publish a release tag only after intentionally choosing the version.
- Keep security disclosures private until coordinated publication.

## Operational limits

The Update Center performs Git fast-forward updates from official
`main`; it is not a signed release verification mechanism.
The static website previews are illustrative, not live security scans.
MForce Academy remains a roadmap, not an accredited training program.
The project's MIT license includes warranty limitations.

## Support and communication

Use GitHub issues for non-sensitive reports. For vulnerabilities, use
private reporting if available. Do not invent a dedicated email,
financial reward, training certificate or maintainer identity.
