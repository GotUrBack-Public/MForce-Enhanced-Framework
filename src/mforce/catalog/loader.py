"""Strict, safe, side-effect-free manifest discovery."""
import json
import re
from pathlib import Path

REQUIRED = {"id", "name", "category", "entry", "enabled", "version",
            "interface", "permission", "description"}
PERMISSIONS = {"local", "passive-network", "authorized-network", "maintenance"}


class CatalogError(ValueError):
    pass


def strict_json(path):
    def pairs_unique(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise CatalogError(f"duplicate JSON key: {key}")
            data[key] = value
        return data
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          object_pairs_hook=pairs_unique)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError(f"{path}: {exc}") from exc


def validate(data):
    if not isinstance(data, dict):
        return ["manifest must be a JSON object"]
    errors = []
    if set(data) != REQUIRED:
        errors.append(f"manifest fields differ: missing={sorted(REQUIRED - set(data))}; extra={sorted(set(data) - REQUIRED)}")
    if not isinstance(data.get("id"), str) or not re.fullmatch(r"[a-z]{3}[0-9]{3}", data["id"]):
        errors.append("invalid module id")
    if not isinstance(data.get("entry"), str) or not re.fullmatch(r"[A-Za-z0-9_-]+\.sh", data["entry"]):
        errors.append("entry must be a simple shell filename")
    if type(data.get("enabled")) is not bool:
        errors.append("enabled must be boolean")
    for key in ("name", "category", "version", "description"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"{key} must be nonempty text")
    if data.get("interface") != "legacy-shell-v1":
        errors.append("unsupported module interface")
    if not isinstance(data.get("permission"), str) or data["permission"] not in PERMISSIONS:
        errors.append("invalid permission label")
    return errors


def load_modules(root):
    root = Path(root).resolve()
    base = root / "src/plugins"
    if not base.is_dir():
        raise CatalogError(f"missing directory: {base}")
    modules = []
    seen = set()
    for path in sorted(base.glob("*/*/manifest.json")):
        if path.is_symlink() or path.parent.is_symlink():
            raise CatalogError(f"symlink manifest: {path}")
        data = strict_json(path)
        errors = validate(data)
        if errors:
            raise CatalogError(f"{path}: {'; '.join(errors)}")
        if (path.parent.name, path.parent.parent.name) != (data["id"], data["category"]):
            raise CatalogError(f"manifest location mismatch: {path}")
        if data["id"] in seen:
            raise CatalogError(f"duplicate module id: {data['id']}")
        seen.add(data["id"])
        modules.append({**data, "manifest": path.relative_to(root).as_posix()})
    return modules
