# Guided Nmap integration

MForce exposes Nmap as an external program through the tool manager. When Nmap is selected, MForce automatically checks whether it is installed and refreshes it to the version available from the system package repositories before showing scan profiles.

## Automatic setup

Supported package managers:
- Termux: `pkg update` and `pkg install nmap`
- Debian / Ubuntu: `apt-get update` and `apt-get install nmap`
- Fedora-family: `dnf upgrade nmap` (or install if missing)
- openSUSE: `zypper refresh` and update/install
- Arch-family: `pacman -Syu --needed nmap`
- Alpine: `apk update` and upgrade/install

On Linux, administrator privileges are required; MForce uses `sudo` when not already running as root. Termux uses its own `pkg` manager. Unsupported systems are reported rather than given a guessed command. Package repository refreshes and upgrades require an internet connection. On Arch, the package operation performs a full system upgrade because partial upgrades are unsupported.

## User workflow

1. Select **Nmap** in the manager with the arrow keys.
2. MForce checks Nmap and installs or updates it using the detected package manager.
3. Select one fixed scan profile with the arrow keys.
4. Enter one IP address or hostname.
5. Press Enter to start or Q to cancel.

There is no command-line or arbitrary flag input in the UI.

## Profiles

| Profile | Fixed arguments | Purpose |
|---|---|---|
| Host discovery | `-sn -T3 --reason --host-timeout 2m` | Check whether a host appears reachable |
| Quick TCP | `-sT -F -T3 --reason --host-timeout 3m` | Check common TCP ports |
| Service check | `-sT -sV --top-ports 100 -T3 --reason --host-timeout 5m` | Identify services on the 100 most common TCP ports |

All profiles are non-privileged connect/discovery scans. They do not use spoofing, evasion, brute force, exploit scripts, or broad port ranges. The adapter accepts one host only; CIDR ranges, wildcards, shell metacharacters, whitespace, and option-like targets are rejected.

## Authorization

Only scan systems you own or have explicit permission to assess. A target being publicly reachable does not imply permission to scan it. Nmap output is shown in the terminal and is not uploaded by this adapter.
