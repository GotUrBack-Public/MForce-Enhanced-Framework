"""Tests for the guided, single-host Nmap adapter."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NmapAdapterTests(unittest.TestCase):
    def run_bash(self, code, *args):
        return subprocess.run(
            ["bash", "-c", code, "test", *args], cwd=ROOT, text=True,
            capture_output=True, timeout=8,
        )

    def test_accepts_ip_and_hostname(self):
        result = self.run_bash(
            'source src/tools/nmap.lib && '
            'mf_nmap_validate_target "$1" && mf_nmap_validate_target "$2"',
            "192.0.2.10", "scan.example.org",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_ranges_and_shell_syntax(self):
        for target in ("192.0.2.0/24", "example.org;id", "-oN/tmp/x", "bad host", "*.example.org"):
            with self.subTest(target=target):
                result = self.run_bash(
                    'source src/tools/nmap.lib && mf_nmap_validate_target "$1"', target,
                )
                self.assertNotEqual(result.returncode, 0)

    def test_profiles_are_fixed_and_bounded(self):
        result = self.run_bash(
            'source src/tools/nmap.lib && '
            'mf_nmap_profile discovery && printf "%s\\n" "${MF_NMAP_ARGS[*]}" && '
            'mf_nmap_profile quick && printf "%s\\n" "${MF_NMAP_ARGS[*]}" && '
            'mf_nmap_profile services && printf "%s\\n" "${MF_NMAP_ARGS[*]}"'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-sn -T3", result.stdout)
        self.assertIn("-sT -F -T3", result.stdout)
        self.assertIn("-sT -sV --top-ports 100", result.stdout)

    def test_nmap_is_registered_in_tool_catalog(self):
        import json
        catalog = json.loads((ROOT / "src/tools/catalog.json").read_text())
        self.assertEqual([item["id"] for item in catalog["tools"]], ["nmap"])
        self.assertEqual(catalog["tools"][0]["command"], "nmap")

    def test_unknown_profile_is_rejected(self):
        result = self.run_bash(
            'source src/tools/nmap.lib && mf_nmap_profile arbitrary'
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
