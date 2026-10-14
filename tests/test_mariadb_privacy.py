"""Privacy regression tests for opt-in, metadata-only MariaDB logging."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "src/core/mariadb.sh"


class DatabasePrivacyTests(unittest.TestCase):
    def run_shell(self, code, **env):
        return subprocess.run(
            ["bash", "-c", f'source "{SCRIPT}"; {code}'],
            capture_output=True, text=True, timeout=10,
            env={**os.environ, **env},
        )

    def test_database_is_off_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_shell(
                'mf_db_start; printf "READY=%s\\n" "${MF_DB_READY:-0}"',
                XDG_STATE_HOME=directory, MF_DB_ENABLE="0",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("READY=0", result.stdout)
            self.assertFalse((Path(directory) / "mforce").exists())

    def test_disabled_overrides_opt_in(self):
        result = self.run_shell(
            'mf_db_start; printf "READY=%s\\n" "${MF_DB_READY:-0}"',
            MF_DB_ENABLE="1", MF_DB_DISABLE="1",
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("READY=0", result.stdout)

    def test_invalid_retention_rejected_before_disk_access(self):
        for retention in ("0", "366", "abc", "1;DROP", "-1"):
            with self.subTest(retention=retention):
                with tempfile.TemporaryDirectory() as directory:
                    result = self.run_shell(
                        "mf_db_start", MF_DB_ENABLE="1",
                        MF_DB_RETENTION_DAYS=retention,
                        XDG_STATE_HOME=directory,
                    )
                    self.assertEqual(result.returncode, 0)
                    self.assertIn("invalid MF_DB_RETENTION_DAYS", result.stderr)
                    self.assertFalse((Path(directory) / "mforce").exists())

    def test_record_never_reads_or_stores_raw_output(self):
        with tempfile.TemporaryDirectory() as directory:
            bin_dir = Path(directory) / "bin"
            bin_dir.mkdir()
            output = Path(directory) / "sql.txt"
            fake = bin_dir / "mariadb"
            fake.write_text('#!/bin/sh\ncat > "$MF_TEST_SQL"\n')
            fake.chmod(0o755)
            socket = Path(directory) / "mysql.sock"
            # Bash -S requires a real Unix-domain socket.
            import socket as sockets
            server = sockets.socket(sockets.AF_UNIX)
            try:
                server.bind(str(socket))
                result = self.run_shell(
                    'MF_DB_READY=1; mf_db_record tcp401 0 /path/to/private/output',
                    MF_DB_SOCKET=str(socket), MF_TEST_SQL=str(output),
                    PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                sql = output.read_text()
                self.assertIn("'tcp401',0,NULL", sql)
                self.assertNotIn("private", sql)
                self.assertNotIn("UNHEX", sql)
            finally:
                server.close()

    def test_record_rejects_untrusted_identifiers(self):
        with tempfile.TemporaryDirectory() as directory:
            import socket as sockets
            sock = sockets.socket(sockets.AF_UNIX)
            path = str(Path(directory) / "mysql.sock")
            try:
                sock.bind(path)
                result = self.run_shell(
                    'MF_DB_READY=1; mf_db_record "x\x27); DROP TABLE x; --" 0',
                    MF_DB_SOCKET=path,
                )
                self.assertEqual(result.returncode, 0)
            finally:
                sock.close()


if __name__ == "__main__":
    unittest.main()
