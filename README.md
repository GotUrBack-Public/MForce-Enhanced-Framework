# MForce Enhanced Framework

<p align="center">
  <img src="assets/banners/logo.png" alt="MForce Enhanced Framework" width="420">
</p>

<p align="center">
  <strong>Next-generation modular framework for Termux.</strong>
</p>

<p align="center">
  <a href="https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/stargazers">
    <img src="https://img.shields.io/github/stars/GotUrBack-Public/MForce-Enhanced-Framework?style=flat-square" alt="Stars">
  </a>
  <a href="https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/GotUrBack-Public/MForce-Enhanced-Framework?style=flat-square" alt="Contributors">
  </a>
  <img src="https://img.shields.io/badge/version-v0.01.2-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/language-Shell-4EAA25?style=flat-square&logo=gnu-bash&logoColor=white" alt="Shell">
  <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="License">
</p>

---

## About

**MForce Enhanced Framework** is a modular framework built specifically for **Termux**.

A complete rebuild of the original MForce architecture  https://github.com/MidnightCoding1/mForce  focused on modularity, a dedicated terminal UI, separated functions and libraries, JSON-based configuration and reusable resources.

## Features

- Modular architecture
- Interactive terminal UI
- Keyboard navigation
- Category and function system
- Separated function libraries
- Central resource libraries
- JSON-based configuration
- Local startup confirmation (not access control)
- Custom color system
- Termux-focused design

## Structure

```text
MForce-Enhanced-Framework/
│
├── xrm742.sh
├── classes1.lib
├── classes2.lib
├── classes3.lib
├── classes4.lib
├── classes5.lib
│
├── src/
│   ├── ui/
│   ├── colors/
│   ├── functions/
│   ├── lib/
│   ├── data/
│   └── auth/
│
├── assets/
│   └── banners/
│
└── cfg/

```

## Installation and startup

In Termux:

```sh
pkg update
pkg install git bash jq coreutils ncurses-utils iproute2
git clone https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git
cd MForce-Enhanced-Framework
bash xrm742.sh
```

The tracked scripts have executable permissions. Internal script transitions use
Bash explicitly. Android properties use `getprop`; unavailable system information
is reported as unavailable. Network interface access can depend on Android's
permissions. No root access is required.

Navigate with arrow keys, Enter and Q. Category Info describes the last highlighted
category (the first category initially). EOF closes the application cleanly.

## Configuration

`cfg/zrk391.json` is the application's version and project metadata source.
`src/auth/ath.json` controls the visible startup confirmation:

- `enabled`: boolean, default `true`; `false` skips the confirmation.
- `max_attempts`: integer 1–100, default 3.
- `code_length`: integer 1–64, default 6, excluding the display separator.
- `case_sensitive`: boolean, default `false`.
- `delay_on_failure`: integer 0–60 seconds, default 2.

Invalid configuration stops startup rather than skipping confirmation. This is
not a user login or access-control system. Each run has its own private temporary
session directory, removed on normal exit and handled termination signals.
SIGKILL, a device crash or power loss cannot run cleanup handlers.

Categories and modules are registered in `src/data/cats.json` and `funcs.json`.
Network Information and System Information are implemented. Connection Test and
OSINT Search remain registered but disabled until their entry scripts exist.
Utilities, Files and Settings currently have no modules. The web files remain
placeholders.

Module `.conf` files are parsed as data, never sourced as shell code. Their
`enabled`, `version` and `mode=terminal` settings are checked against metadata.
Help is available through `bash src/functions/lar386.sh --help` and
`bash src/functions/vkn193.sh --help`.

`src/core/runtime.sh` loads the five shared libraries and provides configuration
validation, common key handling and terminal cleanup. `src/core/schema.jq`
defines the JSON validation rules.

## Validation

Install Python 3 and jq, then run:

```sh
python3 -m unittest discover -s tests -v
```

The tests use temporary repository copies and pseudo-terminals. They cover startup,
configuration failures, navigation, both modules, EOF, terminal restoration and
session cleanup. They run in GitHub Actions on pushes and pull requests. Linux
checks do not replace a smoke test on a real Android/Termux device.
