#!/usr/bin/env python3
"""Bounded TCP connect scanner for authorized security assessments."""
import argparse
import concurrent.futures
import ipaddress
import json
import socket
import sys
import time

DEFAULT_PORTS = "21,22,25,53,80,110,143,443,445,587,993,995,1433,3306,3389,5432,6379,8080,8443"
MAX_PORTS = 128
MAX_WORKERS = 8


def parse_ports(spec):
    ports = set()
    for item in spec.split(","):
        item = item.strip()
        if not item:
            raise ValueError("Empty port entry")
        if "-" in item:
            parts = item.split("-")
            if len(parts) != 2 or not all(p.isdecimal() for p in parts):
                raise ValueError("Invalid port range")
            first, last = map(int, parts)
            if first > last or last - first >= MAX_PORTS:
                raise ValueError("Port range must be ascending and limited")
            ports.update(range(first, last + 1))
        elif item.isdecimal():
            ports.add(int(item))
        else:
            raise ValueError("Invalid port: " + item)
        if len(ports) > MAX_PORTS:
            raise ValueError("Maximum 128 ports per run")
    if not ports or any(p < 1 or p > 65535 for p in ports):
        raise ValueError("Ports must be in 1..65535")
    return sorted(ports)


def resolve_target(target, allow_public):
    """Restrict default scans to loopback and private network addresses."""
    if "://" in target or "/" in target or any(c.isspace() for c in target):
        raise ValueError("Provide a hostname or IP, not a URL or network range")
    results = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
    addresses = sorted({row[4][0] for row in results})
    if not addresses:
        raise ValueError("Target could not be resolved")
    for address in addresses:
        ip = ipaddress.ip_address(address.split("%")[0])
        if ip.is_multicast or ip.is_unspecified or ip.is_reserved or ip.is_link_local:
            raise ValueError("Unsupported target address: " + address)
        if not allow_public and not (ip.is_private or ip.is_loopback):
            raise ValueError("Public targets require --allow-public and authorization")
    return addresses


def probe(address, port, timeout):
    family = socket.AF_INET6 if ":" in address else socket.AF_INET
    started = time.monotonic()
    try:
        with socket.socket(family, socket.SOCK_STREAM) as connection:
            connection.settimeout(timeout)
            result = connection.connect_ex((address, port))
            state = "OPEN" if result == 0 else "CLOSED_OR_FILTERED"
    except (OSError, TimeoutError):
        state = "CLOSED_OR_FILTERED"
    return {"address": address, "port": port, "state": state, "elapsed_ms": round((time.monotonic() - started) * 1000)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="MForce TCP Connect Scan — Educational Purpose / Professional Usage / Authorized Targets Only")
    parser.add_argument("target", nargs="?", help="Hostname or IP; interactive prompt when omitted")
    parser.add_argument("--ports", default=DEFAULT_PORTS, help="Comma-separated ports or short ranges (max 128)")
    parser.add_argument("--timeout", type=float, default=0.7, help="Per-port timeout, 0.2–3 seconds")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent probes, 1–8")
    parser.add_argument("--allow-public", action="store_true", help="Allow explicitly authorized public targets")
    parser.add_argument("--authorized", action="store_true", help="Confirm permission to scan the target")
    parser.add_argument("--json", action="store_true", help="Machine-readable results")
    args = parser.parse_args(argv)
    if not args.target:
        if not sys.stdin.isatty():
            parser.error("target required in noninteractive mode")
        args.target = input("Authorized target (IP / hostname): ").strip()
    if not args.authorized:
        parser.error("Use --authorized only if you own the target or have explicit permission")
    if not 0.2 <= args.timeout <= 3.0 or not 1 <= args.workers <= MAX_WORKERS:
        parser.error("Timeout must be 0.2–3 seconds; workers must be 1–8")
    try:
        ports = parse_ports(args.ports)
        addresses = resolve_target(args.target, args.allow_public)
    except (ValueError, OSError, socket.gaierror) as exc:
        parser.error(str(exc))
    jobs = [(address, port) for address in addresses for port in ports]
    if len(jobs) > 256:
        parser.error("Maximum 256 address/port combinations")
    if not args.json:
        print("MFORCE / TCP CONNECT SCAN")
        print("Educational Purpose | Professional Usage | Authorized Targets Only")
        print("GDPR: obtain a lawful basis, minimize data and avoid unnecessary retention.")
        print("Target: {} | Addresses: {} | Ports: {}".format(args.target, len(addresses), len(ports)))
        print("STATE               ADDRESS                    PORT    TIME")
        print("-" * 67)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda job: probe(*job, args.timeout), jobs))
    results.sort(key=lambda row: (row["address"], row["port"]))
    if args.json:
        print(json.dumps({"target": args.target, "results": results}, indent=2))
    else:
        for result in results:
            print("{:<19} {:<26} {:<7} {}ms".format(result["state"], result["address"], result["port"], result["elapsed_ms"]))
        print("Completed: {} probes; {} open.".format(len(results), sum(r["state"] == "OPEN" for r in results)))
        print("Note: CLOSED_OR_FILTERED does not distinguish rejection from filtering.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
