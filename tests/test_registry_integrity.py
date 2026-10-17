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
