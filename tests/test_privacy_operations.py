"""Tests for the optional manual local SQL retention helper."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/mariadb-retention.sh"


class PrivacyOperationsTests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, timeout=5)

    def test_help_does_not_need_a_database(self):
        p = self.invoke("--help")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("DRY", p.stdout.lower().upper())
        self.assertIn("--execute", p.stdout)

    def test_missing_days_is_rejected(self):
        p = self.invoke("--execute")
        self.assertEqual(p.returncode, 2)
        self.assertIn("--days", p.stderr)

    def test_unsafe_days_are_rejected_before_db_access(self):
        for days in ("0", "-1", "abc", "1;DELETE", "36501", "99999999999999999"):
            with self.subTest(days=days):
                p = self.invoke("--days", days, "--execute")
                self.assertEqual(p.returncode, 2)
                self.assertIn("Specify --days", p.stderr)

    def test_missing_socket_fails_without_deletion(self):
        p = self.invoke("--days", "30", "--socket", "/nonexistent/mforce-test.sock", "--execute")
        self.assertEqual(p.returncode, 1)
        self.assertIn("socket unavailable", p.stderr)

    def test_privacy_docs_disclose_persistence_and_opt_out(self):
        flows = (ROOT / "DSGVO/DATENFLUESSE.md").read_text(encoding="utf-8")
        retention = (ROOT / "DSGVO/LOESCHUNG_UND_AUFBEWAHRUNG.md").read_text(encoding="utf-8")
        self.assertIn("mforce_logs.module_runs", flows)
        self.assertIn("MF_DB_DISABLE=1", flows)
        self.assertIn("MF_DB_DISABLE=1", retention)
        self.assertIn("mariadb-retention.sh", retention)


if __name__ == "__main__":
    unittest.main()
