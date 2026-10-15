"""Cross-platform static parity tests for the separate Windows PowerShell port."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = ROOT / "windows"
REGISTRY = ROOT / "src/data/funcs.json"


class WindowsPortTests(unittest.TestCase):
    def test_native_launcher_is_isolated(self):
        launcher = (WINDOWS / "MForce.ps1").read_text(encoding="utf-8")
        self.assertIn("#requires -Version 7.0", launcher)
        self.assertIn("MForce.Windows.psm1", launcher)
        self.assertNotIn("bash ", launcher.lower())
        self.assertNotIn("wsl ", launcher.lower())

    def test_all_registry_modules_have_mapping(self):
        source = (WINDOWS / "MForce.Windows.psm1").read_text(encoding="utf-8")
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))["functions"]
        ids = {item["id"] for item in registry}
        enabled = {item["id"] for item in registry if item["enabled"]}
        self.assertEqual(len(ids), 23)
        self.assertEqual(len(enabled), 21)
        mapped = dict(re.findall(r"\b([a-z]{3}[0-9]{3})='([^']+)'", source))
        self.assertEqual(set(mapped), ids)
        self.assertEqual({id_ for id_, engine in mapped.items() if engine == "disabled"}, ids - enabled)
        for engine in mapped.values():
            if engine.startswith("python:"):
                self.assertTrue((ROOT / engine.split(":", 1)[1]).is_file())

    def test_safety_and_no_bash_dependency(self):
        source = (WINDOWS / "MForce.Windows.psm1").read_text(encoding="utf-8")
        self.assertIn("requires -Authorized", source)
        self.assertIn("requires -Target", source)
        self.assertIn("not in -ModuleArgs", source)
        self.assertIn("'--apply'", source)
        self.assertNotIn("Invoke-Expression", source)
        self.assertNotIn("iex ", source.lower())
        self.assertNotIn("ExecutionPolicy Bypass", source)
        self.assertNotIn("Start-Process -Verb RunAs", source)

    def test_windows_ci_and_documentation(self):
        self.assertTrue((ROOT / ".github/workflows/windows-powershell.yml").is_file())
        self.assertTrue((WINDOWS / "README.md").is_file())
        self.assertTrue((WINDOWS / "tests/Windows.Tests.ps1").is_file())


if __name__ == "__main__":
    unittest.main()
