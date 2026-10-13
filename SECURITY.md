# Security policy

This project is an early-stage local Termux terminal application. Security fixes
are made against the current default branch; older snapshots are not maintained.
The application version is recorded in `cfg/zrk391.json`.

## Trust boundary

Startup verification asks the user to copy a visible code. It is an interaction
confirmation, not a password, account login, authorization check, or security
boundary. Local scripts remain directly callable. Session JSON is local run
metadata, not an authentication token. Do not use it to authorize access.

Only run code and configuration from trusted sources under your own Termux user.
The framework does not require root. Network and device information are displayed
locally by the existing modules; these modules do not upload their output.

## Reporting

Use GitHub's private vulnerability reporting feature if it is enabled for this
repository. Otherwise, open an issue requesting a private contact method without
including exploit details, credentials, personal data, or sensitive device logs.
Do not post sensitive material in a public issue. No response-time guarantee is
currently offered.
