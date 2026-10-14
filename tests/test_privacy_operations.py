"""Tests for the optional manual local SQL retention helper."""
import os
import socket
import subprocess
import tempfile
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
        self.assertIn("Dry-run", p.stdout)
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

    def test_dry_run_never_deletes_and_execute_is_explicit(self):
        # Exercise SQL construction without requiring a real database service.
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sql_log = root / "queries.txt"
            fake_cli = root / "mariadb"
            fake_cli.write_text(
                """#!/usr/bin/env python3
import os
import sys
from pathlib import Path
query = sys.argv[-1]
with Path(os.environ['MOCK_SQL_LOG']).open('a') as f:
    f.write(query + '\\n')
if query.startswith('SELECT'):
    print('4')
""",
                encoding="utf-8",
            )
            fake_cli.chmod(0o755)
            sock = socket.socket(socket.AF_UNIX)
            sock.bind(str(root / "mysql.sock"))
            try:
                env = {**os.environ, "PATH": f"{root}:{os.environ['PATH']}",
                       "MOCK_SQL_LOG": str(sql_log)}
                cmd = ["bash", str(SCRIPT), "--days", "30", "--socket", str(root / "mysql.sock")]
                dry = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=5)
                self.assertEqual(dry.returncode, 0, dry.stderr)
                self.assertIn("DRY RUN", dry.stdout)
                self.assertEqual(sql_log.read_text().count("SELECT COUNT(*)"), 1)
                self.assertNotIn("DELETE", sql_log.read_text())

                execute = subprocess.run([*cmd, "--execute"], env=env,
                                         capture_output=True, text=True, timeout=5)
                self.assertEqual(execute.returncode, 0, execute.stderr)
                self.assertIn("Retention executed", execute.stdout)
                self.assertEqual(sql_log.read_text().count("DELETE FROM mforce_logs.module_runs"), 1)
                self.assertIn("INTERVAL 30 DAY", sql_log.read_text())
            finally:
                sock.close()

    def test_privacy_docs_disclose_persistence_and_opt_out(self):
        flows = (ROOT / "DSGVO/DATENFLUESSE.md").read_text(encoding="utf-8")
        retention = (ROOT / "DSGVO/LOESCHUNG_UND_AUFBEWAHRUNG.md").read_text(encoding="utf-8")
        self.assertIn("mforce_logs.module_runs", flows)
        self.assertIn("MF_DB_DISABLE=1", flows)
        self.assertIn("MF_DB_DISABLE=1", retention)
        self.assertIn("mariadb-retention.sh", retention)


if __name__ == "__main__":
    unittest.main()
