"""Plugin discovery and CLI smoke tests, with no module execution."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

from src.mforce.catalog.loader import CatalogError, load_modules, validate
from src.mforce.catalog.query import select

ROOT = Path(__file__).resolve().parents[1]


class ModularCatalogTests(unittest.TestCase):
    def test_all_registered_modules_discoverable(self):
        modules = load_modules(ROOT)
        legacy = json.loads((ROOT / "src/data/funcs.json").read_text())["functions"]
        self.assertEqual({m["id"] for m in modules}, {m["id"] for m in legacy})
        self.assertEqual(len(modules), 23)
        self.assertEqual(len(select(modules, enabled_only=True)), 21)
        self.assertEqual(len(select(modules, category="defensive")), 1)

    def test_manifest_validation_rejects_unsafe_paths_and_wrong_types(self):
        valid = load_modules(ROOT)[0].copy()
        valid.pop("manifest")
        self.assertEqual(validate(valid), [])
        for bad in ({"entry": "../escape.sh"}, {"enabled": "true"},
                    {"permission": "superuser"}, {"id": "../../x"}):
            data = {**valid, **bad}
            with self.subTest(bad=bad):
                self.assertTrue(validate(data))

    def test_catalog_json_and_describe_cli(self):
        result = subprocess.run([sys.executable, "-m", "src.mforce", "catalog",
                                 "--enabled-only", "--json"],
                                cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)), 21)
        result = subprocess.run([sys.executable, "-m", "src.mforce", "describe",
                                 "sec601", "--json"],
                                cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["permission"], "local")

    def test_missing_manifest_directory_is_error(self):
        with self.assertRaises(CatalogError):
            load_modules(ROOT / "nonexistent")


if __name__ == "__main__":
    unittest.main()
