"""Compare manifests with legacy registry and metadata; no module execution."""
from pathlib import Path
from ..catalog.loader import CatalogError, load_modules, strict_json
from ..compat.legacy import paths
from ..platform.dependencies import inspect as dependencies
from ..security.policy import expected


def doctor(root, runtime=False):
    root = Path(root).resolve()
    issues = []
    def add(code, path, message, severity="error"):
        issues.append({"severity": severity, "code": code,
                       "path": str(path), "message": str(message)})
    def read(path, key):
        try:
            data = strict_json(root / path)[key]
            if not isinstance(data, list):
                raise ValueError("expected array")
            return data
        except (CatalogError, KeyError, TypeError, ValueError) as exc:
            add("invalid-registry", path, exc)
            return []
    categories = read("src/data/cats.json", "categories")
    registry_entries = read("src/data/funcs.json", "functions")
    category_ids = [c["id"] for c in categories if isinstance(c, dict) and isinstance(c.get("id"), str)]
    if len(category_ids) != len(set(category_ids)):
        add("duplicate-category", "src/data/cats.json", "duplicate category IDs")
    ids = [m["id"] for m in registry_entries if isinstance(m, dict) and isinstance(m.get("id"), str)]
    if len(ids) != len(set(ids)):
        add("duplicate-module", "src/data/funcs.json", "duplicate module IDs")
    registry = {m["id"]: m for m in registry_entries if isinstance(m, dict) and isinstance(m.get("id"), str)}
    for mid, item in registry.items():
        if item.get("category") not in category_ids:
            add("unknown-category", "src/data/funcs.json", mid)
    try:
        modules = load_modules(root)
    except CatalogError as exc:
        add("invalid-manifest", "src/plugins", exc)
        modules = []
    manifest_ids = {m["id"] for m in modules}
    for mid in sorted(set(registry) - manifest_ids):
        add("missing-manifest", "src/plugins", mid)
    for mid in sorted(manifest_ids - set(registry)):
        add("orphan-manifest", "src/plugins", mid)
    for module in modules:
        mid = module["id"]
        if mid not in registry:
            continue
        for key in ("id", "name", "category", "entry", "enabled"):
            if module[key] != registry[mid].get(key):
                add("registry-mismatch", module["manifest"], key)
        if module["permission"] != expected(mid, module["category"]):
            add("permission-mismatch", module["manifest"], "unexpected classification")
        if not module["enabled"]:
            continue
        locations = paths(root, module)
        for kind, path in locations.items():
            if not path.is_file():
                add("missing-legacy-file", path.relative_to(root), kind)
        metadata = locations["metadata"]
        if metadata.is_file():
            try:
                data = strict_json(metadata)
                for key in ("id", "name", "category", "entry", "enabled", "version"):
                    if data.get(key) != module[key]:
                        add("metadata-mismatch", metadata.relative_to(root), key)
            except CatalogError as exc:
                add("invalid-metadata", metadata.relative_to(root), exc)
    host = dependencies() if runtime else None
    if host:
        for name, found in host["required"].items():
            if not found:
                add("missing-command", name, "runtime command unavailable", "warning")
    return {"ok": not any(i["severity"] == "error" for i in issues),
            "checked_modules": len(modules), "issues": issues, "runtime": host}
