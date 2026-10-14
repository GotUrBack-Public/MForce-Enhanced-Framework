#!/usr/bin/env python3
"""Four bounded, authorized HTTP configuration checks; standard library only.

Uses pinned DNS resolution, no redirects, no authentication, no payloads and
never prints cookie values. HEAD is used for path checks (no response body).
"""
from __future__ import annotations

import argparse
import http.client
import ipaddress
import json
import socket
import ssl
import sys
import urllib.parse

MAX_BODY = 4096
PATHS = ("/.env", "/.git/config", "/backup.zip", "/config.json", "/server-status")
ORIGINS = ("https://mforce-audit-a.invalid", "https://mforce-audit-b.invalid")


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, address, hostname, port, timeout):
        super().__init__(hostname, port=port, timeout=timeout, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, self.port), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


def validate_target(url, allow_public):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Provide an absolute http(s) URL")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Credentials and URL fragments are not accepted")
    if len(url) > 2048 or any(ord(c) < 32 for c in url):
        raise ValueError("Invalid or excessively long URL")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    hostname = parsed.hostname
    addresses = set()
    for row in socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM):
        address = row[4][0].split("%")[0]
        ip = ipaddress.ip_address(address)
        if ip.is_multicast or ip.is_unspecified or ip.is_reserved or ip.is_link_local:
            raise ValueError("Unsupported target address")
        addresses.add(ip)
    if not addresses:
        raise ValueError("Target did not resolve")
    if any(ip.is_global for ip in addresses) and any(not ip.is_global for ip in addresses):
        raise ValueError("Mixed public/private DNS resolution is not allowed")
    if any(ip.is_global for ip in addresses) and not allow_public:
        raise ValueError("Public targets require --allow-public and authorization")
    # Pin the actual TCP destination to the IP that passed validation.
    address = str(sorted(addresses, key=lambda ip: (ip.version, int(ip)))[0])
    host_header = hostname if ":" not in hostname else f"[{hostname}]"
    if parsed.port is not None:
        host_header += f":{port}"
    target = parsed.path or "/"
    if parsed.query:
        target += "?" + parsed.query
    return parsed, address, port, host_header, target


def request(parsed, address, port, host_header, target, method, timeout, extra=None):
    if parsed.scheme == "https":
        connection = PinnedHTTPS(address, parsed.hostname, port, timeout)
    else:
        connection = http.client.HTTPConnection(address, port=port, timeout=timeout)
    headers = {"Host": host_header, "User-Agent": "MForce-HTTP-Audit/1.0",
               "Accept": "*/*", "Connection": "close"}
    headers.update(extra or {})
    try:
        connection.request(method, target, headers=headers)
        response = connection.getresponse()
        status = response.status
        headers_list = response.getheaders()
        # Bound reads; no response content is ever displayed or persisted.
        if method != "HEAD":
            response.read(MAX_BODY + 1)
        if status == 429:
            raise ValueError("HTTP 429: rate limited; stopped")
        return status, headers_list
    finally:
        connection.close()


def values(headers, key):
    return [value for name, value in headers if name.lower() == key.lower()]


def cors(parsed, address, port, host, target, timeout):
    findings = []
    for origin in ORIGINS:
        status, headers = request(parsed, address, port, host, target, "GET", timeout,
                                  {"Origin": origin})
        allowed = values(headers, "Access-Control-Allow-Origin")
        credentials = values(headers, "Access-Control-Allow-Credentials")
        reflected = origin in allowed
        findings.append({
            "status": status, "origin_reflected": reflected,
            "wildcard": "*" in allowed,
            "credentials_allowed": any(v.lower().strip() == "true" for v in credentials),
        })
    risk = all(x["origin_reflected"] and x["credentials_allowed"] for x in findings)
    return {"mode": "cors", "requests": 2, "results": findings,
            "review": "Arbitrary origins with credentials accepted" if risk else
            "No confirmed credentialed arbitrary-origin reflection in these probes",
            "warning": "CORS headers alone do not prove cross-origin data exposure."}


def methods(parsed, address, port, host, target, timeout):
    status, headers = request(parsed, address, port, host, target, "OPTIONS", timeout)
    allow = sorted({v.strip().upper() for value in values(headers, "Allow")
                    for v in value.split(",") if v.strip()})
    acam = sorted({v.strip().upper() for value in values(headers, "Access-Control-Allow-Methods")
                   for v in value.split(",") if v.strip()})
    return {"mode": "methods", "requests": 1, "status": status,
            "allow": allow, "cors_allow_methods": acam,
            "warning": "Advertised methods are not proof that a method is usable."}


def cookies(parsed, address, port, host, target, timeout):
    status, headers = request(parsed, address, port, host, target, "GET", timeout)
    found = []
    for value in values(headers, "Set-Cookie")[:20]:
        # Do not report names or values, including potentially sensitive tokens.
        attributes = {part.split("=", 1)[0].strip().lower()
                      for part in value.split(";")[1:]}
        same_site = next((part.split("=", 1)[1].strip().lower()
                          for part in value.split(";")[1:]
                          if part.strip().lower().startswith("samesite=")), None)
        found.append({"secure": "secure" in attributes, "httponly": "httponly" in attributes,
                      "samesite": same_site if same_site in ("lax", "strict", "none") else None,
                      "review": bool(parsed.scheme == "https" and "secure" not in attributes)
                      or "httponly" not in attributes or same_site is None})
    return {"mode": "cookies", "requests": 1, "status": status, "cookies": found,
            "truncated": len(values(headers, "Set-Cookie")) > 20,
            "warning": "Not all cookies require identical flags; review by cookie purpose."}


def paths(parsed, address, port, host, target, timeout):
    results = []
    for path in PATHS:
        status, _ = request(parsed, address, port, host, path, "HEAD", timeout)
        results.append({"path": path, "status": status,
                        "review": status in (200, 206)})
    return {"mode": "paths", "requests": len(results), "results": results,
            "warning": "HEAD 200 can be a generic fallback; no file content was fetched."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("cors", "methods", "cookies", "paths"))
    parser.add_argument("url", help="Explicitly authorized HTTP(S) target")
    parser.add_argument("--authorized", action="store_true")
    parser.add_argument("--allow-public", action="store_true")
    parser.add_argument("--timeout", type=float, default=4.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.authorized:
        parser.error("Explicit permission required: pass --authorized")
    if not 0.5 <= args.timeout <= 8:
        parser.error("Timeout must be between 0.5 and 8 seconds")
    try:
        parsed, address, port, host, target = validate_target(args.url, args.allow_public)
        result = globals()[args.mode](parsed, address, port, host, target, args.timeout)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"MFORCE / {args.mode.upper()} AUDIT — authorized targets only")
            print(json.dumps(result, indent=2))
        return 0
    except (ValueError, OSError, ssl.SSLError, http.client.HTTPException) as exc:
        print(f"HTTP audit stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
