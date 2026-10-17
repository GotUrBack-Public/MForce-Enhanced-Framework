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
