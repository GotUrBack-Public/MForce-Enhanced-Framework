<p align="center">
  <img src="assets/banners/logo.png" alt="MForce — Enhanced Framework" width="100%">
</p>

<p align="center">
  <strong>A modular terminal framework, built for Termux.</strong><br>
  Network visibility. System insight. One consistent interface.
</p>

<p align="center">
  <a href="cfg/zrk391.json"><img src="https://img.shields.io/badge/VERSION-v0.01.2-0b1118?style=flat-square&amp;labelColor=1c2631&amp;color=00b8d9" alt="Version v0.01.2"></a>
  <img src="https://img.shields.io/badge/PLATFORM-Termux-0b1118?style=flat-square&amp;labelColor=1c2631" alt="Platform: Termux">
  <img src="https://img.shields.io/badge/CORE-Bash-0b1118?style=flat-square&amp;labelColor=1c2631" alt="Core: Bash">
  <a href="LICENSE"><img src="https://img.shields.io/badge/LICENSE-MIT-0b1118?style=flat-square&amp;labelColor=1c2631" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> &nbsp; / &nbsp;
  <a href="#capabilities">Capabilities</a> &nbsp; / &nbsp;
  <a href="#architecture">Architecture</a> &nbsp; / &nbsp;
  <a href="#configuration">Configuration</a> &nbsp; / &nbsp;
  <a href="#development">Development</a>
</p>

---

## Overview

**MForce Enhanced Framework** brings network and system information into a keyboard-driven terminal interface. Built in Bash for Termux, it separates navigation, module entry points, reusable libraries and configuration into small, readable components.

A rebuild of the original [mForce](https://github.com/MidnightCoding1/mForce) architecture, focused on a consistent interface and a clear foundation for additional modules.

| Terminal interface | Modular core | Explicit configuration |
| :--- | :--- | :--- |
| Navigate categories, inspect a module, then run it. | Separate entry points, shared libraries and module resources. | JSON registries, validated settings and configurable colors. |

> **Project status · Early development**<br>
> Network Information and System Information are implemented. Additional modules and the web interface are still under development.

## Quick start

Run in **Termux**. Root access is not required.

```bash
pkg update
pkg install git bash jq coreutils ncurses-utils iproute2

git clone https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git
cd MForce-Enhanced-Framework
bash xrm742.sh
```

At startup, enter the displayed confirmation code. Then select a category, open a module preview and press Enter to run it.

| Key | Action |
| :--- | :--- |
| <kbd>↑</kbd> <kbd>↓</kbd> | Move through the menu |
| <kbd>Enter</kbd> | Open the selected item or run the previewed module |
| <kbd>Q</kbd> | Go back; exit from the main menu |

**Category Info** describes the last highlighted category, or the first category initially. Closing standard input exits cleanly.

## Capabilities

| Module | Purpose | Availability |
| :--- | :--- | :--- |
| **Network Information** | Display network interfaces, addresses and hostname. | Available |
| **System Information** | Inspect architecture, kernel, Android version, SDK, device and runtime details. | Available |
| Connection Test | Registered entry for a future connectivity module. | Not implemented · disabled |
| OSINT Search | Registered entry for a future search module. | Not implemented · disabled |

The **Utilities**, **Files** and **Settings** categories are present but contain no modules yet. Web files are placeholders.

<details>
<summary><strong>Module help and platform notes</strong></summary>

```bash
bash src/functions/lar386.sh --help
bash src/functions/vkn193.sh --help
```

Android properties are read through `getprop`. Missing system information is reported as unavailable. Access to network interfaces depends on Android permissions and the device environment.

The existing information modules display their results locally; they do not upload their output.

</details>

## Architecture

The application starts at `xrm742.sh`, displays startup confirmation and opens the category menu. Each module has its own entry point and resource directory.

| Location | Responsibility |
| :--- | :--- |
| [`xrm742.sh`](xrm742.sh) | Application entry point |
| [`src/core/`](src/core/) | Shared runtime, input handling, cleanup and JSON schemas |
| [`src/ui/`](src/ui/) | Startup screen, categories, module selection, previews and About |
| [`src/auth/`](src/auth/) | Visible startup confirmation and local session lifecycle |
| [`src/functions/`](src/functions/) | Module entry scripts |
| [`src/lib/`](src/lib/) | Module implementations, metadata, configuration and help |
| [`src/data/`](src/data/) | Category and function registries |
| [`src/colors/`](src/colors/) | Terminal color definitions and UI roles |
| [`cfg/`](cfg/) | Project metadata and application version |
| `classes1.lib` – `classes5.lib` | Shared file, terminal, JSON, system and text helpers |

## Configuration

Project metadata and the application version live in [`cfg/zrk391.json`](cfg/zrk391.json). Categories and module entries are defined in [`cats.json`](src/data/cats.json) and [`funcs.json`](src/data/funcs.json).

<details>
<summary><strong>Startup confirmation settings</strong> — src/auth/ath.json</summary>

| Setting | Default | Accepted values |
| :--- | :--- | :--- |
| `enabled` | `true` | Boolean; `false` skips confirmation |
| `max_attempts` | `3` | Integer from 1 to 100 |
| `code_length` | `6` | Integer from 1 to 64; excludes the display separator |
| `case_sensitive` | `false` | Boolean |
| `delay_on_failure` | `2` | Integer from 0 to 60 seconds |

Invalid configuration stops startup. Each run creates a private temporary session directory and removes it on normal exit or handled termination signals. Forced termination such as SIGKILL, a device crash or power loss cannot run cleanup handlers.

</details>

<details>
<summary><strong>Module resources and colors</strong></summary>

Module `.conf` files are parsed as data, never executed as shell code. Their `enabled`, `version` and `mode=terminal` settings are checked against module metadata. Existing `.help` files are available through the entry scripts' `--help` option.

[`src/colors/clrs.json`](src/colors/clrs.json) defines terminal colors. The accompanying shell files assign those colors to menus, status messages and interface elements.

</details>

## Development

Install **Python 3** and **jq**, then run the regression suite:

```bash
python3 -m unittest discover -s tests -v
```

Tests use isolated repository copies and pseudo-terminals to exercise startup, configuration failures, navigation, both implemented modules, EOF handling, session isolation and terminal restoration.

| Resource | Description |
| :--- | :--- |
| [Regression suite](tests/test_regression.py) | Automated behavioral and structural checks |
| [CI workflow](.github/workflows/audit.yml) | Configured to run checks on pushes and pull requests |
| [Audit report](docs/AUDIT-2026-10-13.md) | Findings, fixes, validation and remaining limits |
| [Report a bug](https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/issues/new?template=bug_report.md) | Reproduction steps and expected behavior |
| [Suggest a feature](https://github.com/GotUrBack-Public/MForce-Enhanced-Framework/issues/new?template=feature_request.md) | Proposals for the next iteration |

Linux regression checks do not replace testing on an Android device running Termux.

## Security

The visible startup code is an **interaction confirmation**, not a password or access-control boundary. Session JSON contains local run metadata, not an authorization token. Scripts remain directly callable.

See the [security policy](SECURITY.md) for the trust model and reporting guidance. Keep credentials and personal or sensitive device data out of public issues.

---

<p align="center">
  <strong>MFORCE ENHANCED FRAMEWORK</strong><br>
  Built for Termux · Written in Bash · <a href="LICENSE">MIT licensed</a><br>
  <sub>Based on the original <a href="https://github.com/MidnightCoding1/mForce">mForce</a> project.</sub>
</p>
