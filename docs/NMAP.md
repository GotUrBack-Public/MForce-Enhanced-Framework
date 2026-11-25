# Guided Nmap integration

MForce exposes Nmap as an external program through the tool manager. Nmap is managed by the shared startup dependency checker, using its package mappings in `src/tools/catalog.json`.

## User workflow

1. Start the MForce tool manager. It checks dependencies for every enabled registered tool.
2. Select **Nmap** with the arrow keys.
3. Select one fixed scan profile with the arrow keys.
4. Enter one IP address or hostname.
5. Press Enter to start or Q to cancel.

There is no command-line or arbitrary flag input in the UI.

## Profiles

| Profile | Fixed arguments | Purpose |
|---|---|---|
| Host discovery | `-sn -T3 --reason --host-timeout 2m` | Check whether the host appears reachable |
| Quick TCP | `-sT -F -T3 --reason --host-timeout 3m` | Check common TCP ports |
| Service check | `-sT -sV --top-ports 100 -T3 --reason --host-timeout 5m` | Identify services on the 100 most common TCP ports |

All profiles are non-privileged connect/discovery scans. They do not use spoofing, evasion, brute force, exploit scripts, or broad port ranges. The adapter accepts one host only; CIDR ranges, wildcards, shell metacharacters, whitespace, and option-like targets are rejected.

## Authorization

Only scan systems you own or have explicit permission to assess. A target being publicly reachable does not imply permission to scan it. Nmap output is shown in the terminal and is not uploaded by this adapter.
