"""Read-only developer commands; existing interactive CLI stays unchanged."""
import argparse
import json
from pathlib import Path
from .catalog.loader import CatalogError, load_modules
from .catalog.query import select
from .config.paths import root as default_root
from .diagnostics.checks import doctor
from .metrics.counts import measure
from .reports.text import doctor_report


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3 -m src.mforce")
    parser.add_argument("--root", type=Path, default=default_root())
    subs = parser.add_subparsers(dest="command", required=True)
    check = subs.add_parser("doctor", help="Check manifests and shell registry")
    check.add_argument("--json", action="store_true")
    check.add_argument("--runtime", action="store_true")
    catalog = subs.add_parser("catalog", help="List registered plugins")
    catalog.add_argument("--category")
    catalog.add_argument("--enabled-only", action="store_true")
    catalog.add_argument("--json", action="store_true")
    describe = subs.add_parser("describe", help="Describe one plugin without executing it")
    describe.add_argument("id")
    describe.add_argument("--json", action="store_true")
    stats = subs.add_parser("stats", help="Track file and folder milestones")
    stats.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "doctor":
        data = doctor(root, runtime=args.runtime)
        print(json.dumps(data, indent=2) if args.json else doctor_report(data))
        return 0 if data["ok"] else 1
    if args.command == "stats":
        data = measure(root)
        if args.json:
            print(json.dumps(data, indent=2))
        else:
            print(f"Files: {data['files']}/500; folders: {data['directories']}/150")
            print(f"Remaining: {data['remaining']['files']} files, {data['remaining']['directories']} folders")
        return 0
    try:
        modules = load_modules(root)
    except CatalogError as exc:
        parser.exit(1, f"Catalog error: {exc}\n")
    if args.command == "catalog":
        chosen = select(modules, args.category, args.enabled_only)
        if args.json:
            print(json.dumps(chosen, indent=2))
        else:
            for module in chosen:
                print(f"{module['id']} [{module['category']}] {module['name']} "
                      f"({'enabled' if module['enabled'] else 'disabled'})")
        return 0
    module = next((m for m in modules if m["id"] == args.id), None)
    if module is None:
        parser.exit(2, f"Unknown module: {args.id}\n")
    if args.json:
        print(json.dumps(module, indent=2))
    else:
        for key, value in module.items():
            print(f"{key}: {value}")
    return 0
