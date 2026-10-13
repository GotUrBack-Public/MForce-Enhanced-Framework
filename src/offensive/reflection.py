#!/usr/bin/env python3
"""MForce HTTP Reflection Inspector — bounded, authorized active GET check.

Only a harmless unique alphanumeric marker is transmitted, never XSS code.
A reflected marker is not evidence of executable XSS.
"""
from __future__ import annotations

import argparse
import html
import ipaddress
import json
import re
import secrets
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser


MAX_BODY = 256 * 1024
MAX_PARAMS = 8
MAX_REQUESTS = 9
USER_AGENT = "MForce-ReflectionInspector/1.0 (+authorized-security-review)"


def validate_url(raw: str, allow_public: bool) -> tuple[str, str]:
    parsed = urllib.parse.urlsplit(raw)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Target must be an absolute http(s) URL")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Credentials and fragments are not accepted")
    if parsed.port is not None and not (1 <= parsed.port <= 65535):
        raise ValueError("Invalid port")
    hostname = parsed.hostname
    if hostname.lower() in ("localhost", "localhost.localdomain"):
        return raw, hostname
    try:
        addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(
            hostname, parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM
        )}
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed: {exc}") from exc
    if not addresses:
        raise ValueError("No resolved addresses")
    if any(not ip.is_global for ip in addresses) and any(ip.is_global for ip in addresses):
        raise ValueError("Mixed public/private DNS resolution is not accepted")
    if any(ip.is_global for ip in addresses) and not allow_public:
        raise ValueError("Public hosts require --allow-public and explicit authorization")
    if any(ip.is_multicast or ip.is_unspecified or ip.is_reserved for ip in addresses):
        raise ValueError("Unsupported address type")
    return raw, hostname


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fetch(url: str, timeout: float) -> tuple[int, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain;q=.9,*/*;q=.2"})
    opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    try:
        with opener.open(req, timeout=timeout) as response:
            data = response.read(MAX_BODY + 1)
            if len(data) > MAX_BODY:
                raise ValueError("Response exceeded 256 KiB safety limit")
            charset = response.headers.get_content_charset() or "utf-8"
            return response.status, response.headers.get("Content-Type", ""), data.decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code in (301, 302, 303, 307, 308):
            raise ValueError("Redirect not followed; provide the exact authorized URL") from exc
        if exc.code == 429:
            raise ValueError("HTTP 429 rate-limit signal; stopping immediately") from exc
        raise ValueError(f"HTTP {exc.code}; stopping") from exc


class ReflectionHTML(HTMLParser):
    def __init__(self, marker: str):
        super().__init__(convert_charrefs=True)
        self.marker = marker
        self.found: set[str] = set()

    def handle_data(self, data):
        if self.marker in data:
            self.found.add("html_text")

    def handle_comment(self, data):
        if self.marker in data:
            self.found.add("html_comment")

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if value and self.marker in value:
                self.found.add(f"attribute:{key}")


def classify(body: str, marker: str, content_type: str) -> list[str]:
    contexts: set[str] = set()
    if marker not in body and marker not in html.unescape(body):
        return []
    if "html" in content_type.lower():
        parser = ReflectionHTML(marker)
        parser.feed(body)
        contexts |= parser.found
        if re.search(r"<script\b[^>]*>[\s\S]*?" + re.escape(marker), body, re.I):
            contexts.add("script_block")
        if not contexts:
            contexts.add("html_other")
    else:
        contexts.add("text_or_json")
    return sorted(contexts)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Authorized bounded HTTP GET parameter reflection checks")
    parser.add_argument("url", help="Authorized http(s) URL with optional query parameters")
    parser.add_argument("--authorized", action="store_true", help="Confirm permission to test this URL")
    parser.add_argument("--allow-public", action="store_true", help="Permit explicitly authorized public hosts")
    parser.add_argument("--param", action="append", help="Parameter name; repeat for multiple (max 8)")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.authorized:
        parser.error("Use --authorized only when you own or have explicit permission for the target")
    if not 0.5 <= args.timeout <= 10:
        parser.error("Timeout must be between 0.5 and 10 seconds")
    try:
        validate_url(args.url, args.allow_public)
        parsed = urllib.parse.urlsplit(args.url)
        original = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if len(original) > 40:
            raise ValueError("Too many existing query parameters")
        names = list(dict.fromkeys(args.param or [key for key, _ in original]))
        if not names:
            raise ValueError("Specify at least one --param or include query parameters in the URL")
        if len(names) > MAX_PARAMS:
            raise ValueError(f"Maximum {MAX_PARAMS} parameters per run")
        if any(not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", name) for name in names):
            raise ValueError("Parameter names must be 1-64 simple ASCII characters")
        results = []
        for name in names:
            marker = "MFORCE" + secrets.token_hex(8).upper()
            query = [(key, value) for key, value in original if key != name]
            query.append((name, marker))
            target = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", urllib.parse.urlencode(query), ""))
            # No follow redirects, no POSTs, no authentication, no payload execution.
            status, content_type, body = fetch(target, args.timeout)
            contexts = classify(body, marker, content_type)
            results.append({"parameter": name, "reflected": bool(contexts), "contexts": contexts, "status": status})
        report = {"url": urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "")),
                  "tested_parameters": len(results), "requests": len(results), "findings": results,
                  "warning": "Reflection is NOT proof of XSS; no exploit payloads were sent."}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("MFORCE / HTTP REFLECTION INSPECTOR\nEducational Purpose · Professional Usage · Authorized Targets Only")
            for item in results:
                label = ", ".join(item["contexts"]) if item["contexts"] else "not reflected"
                print(f'{item["parameter"]}: {label} (HTTP {item["status"]})')
            print(report["warning"])
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"Reflection check stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
