# MForce security integrations

This PR adds a Renovate configuration and CI checks for ShellCheck, Bandit and Semgrep.

## Enable separately in GitHub settings
- Enable **CodeQL default setup** under Settings > Advanced Security.
- Enable **Dependabot alerts**, **Dependabot security updates**, **secret scanning**, and **push protection** where available.
- Configure a ruleset for main: require pull requests, reviews, passing checks, block force pushes and deletions.
- Configure private vulnerability reporting.

## External apps (manual authorization required)
- Renovate GitHub App: https://github.com/apps/renovate
- Snyk: https://snyk.io/
- Socket: https://socket.dev/
- SonarQube Cloud: https://sonarcloud.io/
- Semgrep AppSec Platform (optional; CLI is included): https://semgrep.dev/
- Gitleaks: https://github.com/gitleaks/gitleaks
- OSV-Scanner: https://github.com/google/osv-scanner

Do not install multiple overlapping dependency update bots without deciding ownership of ecosystems. Dependabot already manages GitHub Actions here; Renovate can be configured to exclude that manager.

## Security review
Review and pin third-party GitHub Actions to full commit SHAs before treating this as production-hardened. Test workflows on this PR, triage findings, and never auto-merge security fixes without tests and review. Avoid giving untrusted pull-request code write tokens or repository secrets.
