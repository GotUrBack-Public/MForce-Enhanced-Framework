"""Catch silent JSON key collisions and broken MForce module registration."""
import json
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


class RegistryIntegrityTests(unittest.TestCase):
    def test_unique_json_keys(self):
        for path in (ROOT / "src/data/cats.json", ROOT / "src/data/funcs.json"):
            with self.subTest(path=path.name):
                strict_json(path)

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
