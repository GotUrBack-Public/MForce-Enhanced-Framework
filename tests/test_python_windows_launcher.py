"""Static checks for the Python-only Windows entry point."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PythonWindowsLauncherTests(unittest.TestCase):
    def test_launcher_exists_and_has_no_shell_dependency(self):
        code = (ROOT / "MForce").read_text(encoding="utf-8")
        self.assertIn('if __name__ == "__main__":', code)
        self.assertIn("msvcrt.getwch()", code)
        self.assertNotIn("shell=True", code)
        self.assertNotIn("bash -c", code)
        self.assertNotIn("wsl.exe", code)

    def test_enabled_modules_are_mapped(self):
        code = (ROOT / "MForce").read_text(encoding="utf-8")
        registry = json.loads((ROOT / "src/data/funcs.json").read_text(encoding="utf-8"))
        enabled = [item for item in registry["functions"] if item["enabled"]]
        self.assertEqual(len(enabled), 21)
        for item in enabled:
            self.assertIn('"' + item["id"] + '"', code)

    def test_engine_files_present(self):
        for path in (
            "src/osint/inspect.py", "src/offensive/tcp_scan.py",
            "src/offensive/xss_lab.py", "src/offensive/reflection.py",
            "src/offensive/http_audit.py", "src/defensive/secrets_audit.py"
        ):
            self.assertTrue((ROOT / path).is_file(), path)


if __name__ == "__main__":
    unittest.main()
