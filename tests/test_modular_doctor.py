"""Compatibility diagnostics catch drift without touching the real registry."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.mforce.diagnostics.checks import doctor

ROOT = Path(__file__).resolve().parents[1]


class ModularDoctorTests(unittest.TestCase):
    def test_real_repository_passes_integrity_checks(self):
        report = doctor(ROOT)
        self.assertTrue(report["ok"], report["issues"])
        self.assertEqual(report["checked_modules"], len(json.loads((ROOT / "src/data/funcs.json").read_text())["functions"]))

    def test_mismatch_and_missing_wrapper_are_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data = root / "src/data"
            data.mkdir(parents=True)
            (data / "cats.json").write_text(json.dumps({"categories": [
                {"id": "net", "name": "Network", "enabled": True}]}))
            (data / "funcs.json").write_text(json.dumps({"functions": [
                {"id": "abc123", "entry": "abc123.sh", "name": "Example",
                 "category": "net", "enabled": True}]}))
            plugin = root / "src/plugins/net/abc123"
            plugin.mkdir(parents=True)
            (plugin / "manifest.json").write_text(json.dumps({
                "id": "abc123", "entry": "abc123.sh", "name": "Example",
                "category": "net", "enabled": True, "version": "1.0.0",
                "interface": "legacy-shell-v1", "permission": "passive-network",
                "description": "A local fixture for registry validation"}))
            report = doctor(root)
            self.assertFalse(report["ok"])
            self.assertIn("missing-legacy-file", {i["code"] for i in report["issues"]})
            content = json.loads((plugin / "manifest.json").read_text())
            content["enabled"] = False
            (plugin / "manifest.json").write_text(json.dumps(content))
            report = doctor(root)
            self.assertIn("registry-mismatch", {i["code"] for i in report["issues"]})

    def test_doctor_cli_machine_output(self):
        result = subprocess.run([sys.executable, "-m", "src.mforce", "doctor",
                                 "--json"], cwd=ROOT, capture_output=True,
                                text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue(json.loads(result.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
