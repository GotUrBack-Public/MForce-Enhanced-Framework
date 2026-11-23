# External Tool Manager

MForce's terminal interface is a control layer for separately installed command-line programs. Tool implementations do not belong in the menu code.

## Current state

- The new interface is launched after the existing local session check.
- The old built-in module list is no longer displayed by the active interface.
- External programs are described in `src/tools/catalog.json`.
- Nmap is registered as the first external tool. It is detected on `PATH` and is never silently installed.
- The manager detects whether a registered executable is available on `PATH`.
- Navigation supports Up/Down, J/K, Home/End, Enter, Q and the existing keyboard help.

## Catalog format

Each tool entry has these fields:

- `id`: unique lowercase identifier.
- `name`: display name.
- `command`: executable name only (no path, shell syntax or arguments).
- `category`: grouping label.
- `description`: short purpose.
- `enabled`: whether the manager may expose the tool.

Example (documentation only):

```json
{
  "schema_version": 1,
  "tools": [
    {
      "id": "nmap",
      "name": "Nmap",
      "command": "nmap",
      "category": "network",
      "description": "Network discovery and security auditing for authorized systems.",
      "enabled": true
    }
  ]
}
```

## Process boundary

The shared adapter `mf_tool_run ID ARG...` accepts only a registered, enabled tool. It checks the executable and invokes it as an argument array. It does not use `eval`, construct a shell command, or interpret a command string. Tool-specific argument forms, authorization checks, output handling, and cancellation will be implemented in each adapter before a tool is exposed for execution.

## First integrated tool: Nmap

See [NMAP.md](NMAP.md) for the arrow-key workflow, fixed scan profiles, target validation, and installation instructions. The interface accepts only one IP address or hostname and does not accept arbitrary command flags.

## Add a tool

1. Install the program separately using its official distribution instructions.
2. Add a validated entry to `src/tools/catalog.json`.
3. Implement a dedicated adapter that validates user input and constructs a safe argument array.
4. Add tests for missing executables, malformed catalog entries, argument handling and cancellation.
5. Only then expose the launch action in the UI.
