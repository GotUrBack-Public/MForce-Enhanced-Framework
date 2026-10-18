import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def strict_json(path):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key {key!r} in {path}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)



REQUIRED_CATEGORY_FIELDS = {
    "id": str,
    "name": str,
    "enabled": bool,
}


def validate_category_registry(data, source_name="categories"):
    """Validate category registry against expected schema, types, and uniqueness."""
    if not isinstance(data, dict) or "categories" not in data:
        raise ValueError(f"{source_name}: missing root 'categories' object")
    if not isinstance(data["categories"], list):
        raise TypeError(f"{source_name}: 'categories' must be a list")

    seen_ids = set()
    for index, item in enumerate(data["categories"]):
        if not isinstance(item, dict):
            raise TypeError(f"{source_name}[{index}]: category entry must be a dictionary")
        for field, expected_type in REQUIRED_CATEGORY_FIELDS.items():
            if field not in item:
                raise ValueError(
                    f"{source_name}[{index}]: missing required field {field!r} in {item}"
                )
            val = item[field]
            if expected_type is bool:
                if not isinstance(val, bool):
                    raise TypeError(
                        f"{source_name}[{index}]: field {field!r} must be bool, got {type(val).__name__}"
                    )
            elif expected_type is str:
                if not isinstance(val, str) or not val.strip():
                    raise TypeError(
                        f"{source_name}[{index}]: field {field!r} must be non-empty string, got {val!r}"
                    )
            elif not isinstance(val, expected_type):
                raise TypeError(
                    f"{source_name}[{index}]: field {field!r} must be {expected_type.__name__}, got {type(val).__name__}"
                )

        cat_id = item["id"]
        if cat_id in seen_ids:
            raise ValueError(
                f"{source_name}[{index}]: duplicate category identifier {cat_id!r}"
            )
        seen_ids.add(cat_id)
    return seen_ids


def check_category_references(functions, categories):
    """Verify that all function entries reference an existing category."""
    valid_categories = {item["id"] for item in categories if isinstance(item, dict) and "id" in item}
    errors = []
    for fn in functions:
        mod_id = fn.get("id", "<unknown>")
        category = fn.get("category")
        if category not in valid_categories:
            errors.append(f"Module {mod_id!r} references nonexistent category {category!r}")
    return errors


def check_entrypoint_permissions(entrypoint_paths, git_root=None):
    """Check that all given entry points have executable file permissions and git mode."""
    issues = []
    for path in entrypoint_paths:
        if not path.is_file():
            issues.append(f"{path}: not a regular file")
        elif not os.access(path, os.X_OK):
            issues.append(f"{path}: missing executable permissions (chmod +x required)")

    if git_root and (Path(git_root) / ".git").exists():
        rel_paths = [str(p.relative_to(git_root)) for p in entrypoint_paths]
        result = subprocess.run(
            ["git", "-C", str(git_root), "ls-files", "-s", *rel_paths],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.strip().splitlines():
            if not line:
                continue
            parts = line.split()
            mode = parts[0]
            rel_file = parts[3]
            if mode != "100755":
                issues.append(f"{rel_file}: git index mode is {mode}, expected 100755")
    return issues


class RegistryIntegrityTests(unittest.TestCase):
    def test_unique_json_keys(self):
        for path in (ROOT / "src/data/cats.json", ROOT / "src/data/funcs.json"):
            with self.subTest(path=path.name):
                strict_json(path)

    def test_category_registry_schema(self):
        cats_path = ROOT / "src/data/cats.json"
        data = strict_json(cats_path)
        category_ids = validate_category_registry(data, cats_path.name)
        self.assertGreater(len(category_ids), 0)

    def test_category_registry_schema_fixtures(self):
        with self.assertRaisesRegex(ValueError, "missing root 'categories'"):
            validate_category_registry({"invalid": []})

        with self.assertRaisesRegex(TypeError, "'categories' must be a list"):
            validate_category_registry({"categories": "not-a-list"})

        with self.assertRaisesRegex(ValueError, "missing required field 'name'"):
            validate_category_registry({
                "categories": [{"id": "net", "enabled": True}]
            })

        with self.assertRaisesRegex(TypeError, "field 'enabled' must be bool"):
            validate_category_registry({
                "categories": [{"id": "net", "name": "Network", "enabled": 1}]
            })

        with self.assertRaisesRegex(TypeError, "field 'enabled' must be bool"):
            validate_category_registry({
                "categories": [{"id": "net", "name": "Network", "enabled": "true"}]
            })

        with self.assertRaisesRegex(TypeError, "field 'id' must be non-empty string"):
            validate_category_registry({
                "categories": [{"id": 123, "name": "Network", "enabled": True}]
            })

        with self.assertRaisesRegex(TypeError, "field 'id' must be non-empty string"):
            validate_category_registry({
                "categories": [{"id": "", "name": "Network", "enabled": True}]
            })

        with self.assertRaisesRegex(ValueError, "duplicate category identifier 'net'"):
            validate_category_registry({
                "categories": [
                    {"id": "net", "name": "Network", "enabled": True},
                    {"id": "net", "name": "Network 2", "enabled": False},
                ]
            })

    def test_registry_category_references_have_no_orphans(self):
        cats = strict_json(ROOT / "src/data/cats.json")["categories"]
        funcs = strict_json(ROOT / "src/data/funcs.json")["functions"]
        errors = check_category_references(funcs, cats)
        self.assertEqual(errors, [], f"Orphaned modules found: {errors}")

    def test_registry_category_references_invalid_fixture(self):
        valid_cats = [{"id": "net", "name": "Network", "enabled": True}]
        synthetic_funcs = [
            {"id": "mod_ok", "category": "net", "enabled": True},
            {"id": "mod_orphan1", "category": "ghost_category", "enabled": True},
            {"id": "mod_orphan2", "category": None, "enabled": False},
        ]
        errors = check_category_references(synthetic_funcs, valid_cats)
        self.assertEqual(len(errors), 2)
        self.assertIn("Module 'mod_orphan1' references nonexistent category 'ghost_category'", errors[0])
        self.assertIn("Module 'mod_orphan2' references nonexistent category None", errors[1])

    def test_public_module_entrypoints_shell_syntax(self):
        entrypoints = sorted((ROOT / "src/functions").glob("*.sh"))
        self.assertGreater(len(entrypoints), 0)
        for path in entrypoints:
            with self.subTest(entrypoint=path.name):
                result = subprocess.run(
                    ["bash", "-n", str(path)],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"Shell syntax error in {path.name}: {result.stderr}",
                )

    def test_shell_syntax_check_detects_syntax_errors(self):
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as tmp:
            tmp.write("if true then echo bad fi\n")
            tmp_path = Path(tmp.name)
        try:
            result = subprocess.run(
                ["bash", "-n", str(tmp_path)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(result.stderr)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_public_shell_entrypoints_executable_mode(self):
        entrypoints = sorted((ROOT / "src/functions").glob("*.sh"))
        self.assertGreater(len(entrypoints), 0)
        issues = check_entrypoint_permissions(entrypoints, git_root=ROOT)
        self.assertEqual(issues, [], f"Public entrypoints with permission issues: {issues}")

    def test_entrypoint_permissions_fixture_detects_non_executable(self):
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as tmp:
            tmp.write("#!/bin/sh\nexit 0\n")
            tmp_path = Path(tmp.name)
        try:
            os.chmod(tmp_path, 0o644)
            issues = check_entrypoint_permissions([tmp_path])
            self.assertEqual(len(issues), 1)
            self.assertIn("missing executable permissions", issues[0])
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_every_enabled_module_has_entry_and_category(self):
        categories = {item["id"] for item in strict_json(ROOT / "src/data/cats.json")["categories"]}
        entries = strict_json(ROOT / "src/data/funcs.json")["functions"]
        self.assertEqual(len(entries), len({item["id"] for item in entries}))
        for item in entries:
            with self.subTest(module=item["id"]):
                self.assertIn(item["category"], categories)
                if item["enabled"]:
                    self.assertTrue((ROOT / "src/functions" / item["entry"]).is_file())

    def test_updater_and_scanner_are_independent(self):
        entries = {item["id"]: item for item in strict_json(ROOT / "src/data/funcs.json")["functions"]}
        self.assertEqual(entries["tcp401"]["category"], "offensive")
        self.assertEqual(entries["tcp401"]["entry"], "tcp401.sh")
        self.assertEqual(entries["upd501"]["category"], "upd")
        self.assertEqual(entries["upd501"]["entry"], "upd501.sh")
        self.assertTrue(entries["tcp401"]["enabled"])
        self.assertTrue(entries["upd501"]["enabled"])


if __name__ == "__main__":
    unittest.main()
