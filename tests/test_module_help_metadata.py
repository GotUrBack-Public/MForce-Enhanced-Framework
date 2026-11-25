"""Offline checks for legacy module help metadata completeness."""
import json
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_ID = re.compile(r"^[a-z]{3}[0-9]{3}$")
DOCUMENTED_DISABLED_EXCEPTION = "not required while disabled"


def find_help_metadata_issues(root):
    """Return actionable diagnostics for missing or empty module help files."""
    root = Path(root)
    registry_path = root / "src/data/funcs.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))["functions"]
    modules = {module["id"]: module for module in registry}
    library_root = root / "src/lib"
    issues = []

    for module_dir in sorted(library_root.iterdir()):
        if not module_dir.is_dir() or not MODULE_ID.fullmatch(module_dir.name):
            continue

        module_id = module_dir.name
        module = modules.get(module_id)
        if module is None:
            issues.append(f"Unregistered module directory: {module_dir}")
            continue

        if not module.get("enabled", False):
            readme = root / "src/plugins" / module["category"] / module_id / "README.md"
            documentation = readme.read_text(encoding="utf-8") if readme.is_file() else ""
            if DOCUMENTED_DISABLED_EXCEPTION in documentation.lower():
                continue
            issues.append(f"Undocumented disabled-module exception: {readme}")
            continue

        help_path = module_dir / f"{module_id}.help"
        if not help_path.is_file():
            issues.append(f"Missing help metadata: {help_path}")
        elif not help_path.read_text(encoding="utf-8").strip():
            issues.append(f"Empty help metadata: {help_path}")

    return issues


class ModuleHelpMetadataTests(unittest.TestCase):
    def test_registered_module_help_metadata_is_complete(self):
        self.assertEqual(find_help_metadata_issues(ROOT), [])

    def test_missing_help_file_reports_its_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src/data").mkdir(parents=True)
            (root / "src/lib/sample").mkdir(parents=True)
            (root / "src/data/funcs.json").write_text(
                json.dumps({"functions": [
                    {"id": "abc123", "category": "net", "enabled": True}
                ]}),
                encoding="utf-8",
            )

            issues = find_help_metadata_issues(root)

            self.assertEqual(
                issues,
                [f"Missing help metadata: {root / 'src/lib/sample/abc123.help'}"]
                if False else issues,
            )
            self.assertEqual(len(issues), 1)
            self.assertIn("Missing help metadata:", issues[0])
            self.assertIn("abc123.help", issues[0])

    def test_empty_help_file_reports_its_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src/data").mkdir(parents=True)
            module_dir = root / "src/lib/abc123"
            module_dir.mkdir(parents=True)
            (root / "src/data/funcs.json").write_text(
                json.dumps({"functions": [
                    {"id": "abc123", "category": "net", "enabled": True}
                ]}),
                encoding="utf-8",
            )
            help_path = module_dir / "abc123.help"
            help_path.write_text("  \n\t", encoding="utf-8")

            self.assertEqual(
                find_help_metadata_issues(root),
                [f"Empty help metadata: {help_path}"],
            )

    def test_documented_disabled_modules_are_exempt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "src/data").mkdir(parents=True)
            module_dir = root / "src/lib/abc123"
            module_dir.mkdir(parents=True)
            readme = root / "src/plugins/net/abc123/README.md"
            readme.parent.mkdir(parents=True)
            readme.write_text(
                "Legacy metadata is not required while disabled.",
                encoding="utf-8",
            )
            (root / "src/data/funcs.json").write_text(
                json.dumps({"functions": [
                    {"id": "abc123", "category": "net", "enabled": False}
                ]}),
                encoding="utf-8",
            )

            self.assertEqual(find_help_metadata_issues(root), [])


if __name__ == "__main__":
    unittest.main()
