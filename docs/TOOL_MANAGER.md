# External Tool Manager

MForce's terminal interface is a control layer for separately installed command-line programs. Tool implementations do not belong in the menu code.

## Startup dependency management

When the tool manager starts, it checks every enabled tool registered in `src/tools/catalog.json`. Each entry declares its required package names for supported package managers. MForce refreshes package metadata, installs missing packages, and upgrades configured packages before showing the menu.

Supported managers: Termux `pkg`, Debian-family `apt`, Fedora-family `dnf`, openSUSE `zypper`, Arch-family `pacman`, and Alpine `apk`. Linux package operations require root or `sudo`. Arch uses a full system upgrade because partial upgrades are unsupported. Termux refreshes and upgrades its package environment. If dependency management fails, MForce reports the error and still opens the manager.

Package mappings are arrays so a tool can declare multiple dependencies:

```json
"packages": {
  "termux": ["nmap", "python"],
  "apt": ["nmap", "python3"],
  "dnf": ["nmap", "python3"],
  "zypper": ["nmap", "python3"],
  "pacman": ["nmap", "python"],
  "apk": ["nmap", "python3"]
}
```

Package names are restricted by catalog validation and are never accepted from user input. Every new tool must include package mappings for the systems it supports.

## Current state

- External programs are described in `src/tools/catalog.json`.
- Nmap is registered as the first external tool.
- The manager detects whether a registered executable is available on `PATH`.
- Navigation supports Up/Down, J/K, Home/End, Enter, Q and keyboard help.

## Process boundary

The shared adapter `mf_tool_run ID ARG...` accepts only a registered, enabled tool. It checks the executable and invokes it as an argument array. It does not use `eval` or interpret a command string.

## Add a tool

1. Add a validated entry to `src/tools/catalog.json`, including package arrays for supported systems.
2. Implement a dedicated adapter that validates user input and constructs a safe argument array.
3. Add tests for missing executables, malformed catalog entries, dependency metadata, argument handling and cancellation.
4. Only then expose the launch action in the UI.
