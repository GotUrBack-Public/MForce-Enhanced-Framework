#!/usr/bin/env python3
"""Offline, bounded local secret-pattern review. Never prints secret values."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

RULES = {
    "private_key_marker": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(rb"\b(?:ghp_|gho_|ghu_|ghs_|ghr_)[A-Za-z0-9]{20,}\b"),
    "aws_access_key_id": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "generic_credential_assignment": re.compile(
        rb"(?i)\b(?:password|passwd|api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
}
SKIP = frozenset({".git", ".venv", "node_modules", "__pycache__", ".tox"})
MAX_FILES = 250
MAX_FILE_SIZE = 1024 * 1024
MAX_FINDINGS = 100


def scan(root: Path):
    if root.is_symlink() or not root.exists():
        raise ValueError("Target must exist and must not be a symlink")
    if root.is_file():
        paths = [root]
        base = root.parent
    elif root.is_dir():
        base = root
        paths = sorted((p for p in root.rglob("*")
                        if p.is_file() and not p.is_symlink()
                        and not any(part in SKIP for part in p.relative_to(root).parts)),
                       key=lambda p: str(p))
    else:
        raise ValueError("Target must be a regular file or directory")
    if len(paths) > MAX_FILES:
        raise ValueError(f"Too many files: maximum {MAX_FILES}")
    findings = []
    checked = 0
    skipped_large = 0
    for path in paths:
        if path.stat().st_size > MAX_FILE_SIZE:
            skipped_large += 1
            continue
        checked += 1
        with path.open("rb") as handle:
            for number, line in enumerate(handle, 1):
                for rule, pattern in RULES.items():
                    if pattern.search(line):
                        findings.append({"file": str(path.relative_to(base)),
                                         "line": number, "rule": rule})
                        if len(findings) >= MAX_FINDINGS:
                            return {"checked_files": checked, "skipped_large": skipped_large,
                                    "findings": findings, "truncated": True}
    return {"checked_files": checked, "skipped_large": skipped_large,
            "findings": findings, "truncated": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Local file or folder; no network access")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = scan(Path(args.path).expanduser())
    except (ValueError, OSError) as exc:
        print(f"Local audit stopped: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("MFORCE / LOCAL SECRET PATTERN AUDIT — OFFLINE")
        print(f"Checked {report['checked_files']} files; {len(report['findings'])} pattern matches")
        for item in report["findings"]:
            print(f"{item['file']}:{item['line']}: {item['rule']}")
        print("Potential matches need manual review. Secret values are never printed.")
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
