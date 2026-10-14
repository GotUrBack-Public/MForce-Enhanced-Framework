"""Smoke test the offline package installer in a temporary sandbox."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackageInstallTests(unittest.TestCase):
    def test_offline_install_creates_launcher_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "unpacked"
            (package / "packaging").mkdir(parents=True)
            (package / "src" / "data").mkdir(parents=True)
            shutil.copy2(ROOT / "packaging/install-local.sh",
                         package / "packaging" / "install-local.sh")
            (package / "src" / "data" / "funcs.json").write_text('{"functions": []}\n')
            (package / "xrm742.sh").write_text(
                '#!/usr/bin/env bash\nprintf "offline-ok\\n"\n')
            destination = root / "installed"
            bin_dir = root / "bin"
            env = {**os.environ, "MFORCE_INSTALL_DIR": str(destination),
                   "MFORCE_BIN_DIR": str(bin_dir)}
            cmd = ["bash", str(package / "packaging" / "install-local.sh")]
            first = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=8)
            self.assertEqual(first.returncode, 0, first.stderr)
            launcher = subprocess.run([str(bin_dir / "mforce")], env=env,
                                      capture_output=True, text=True, timeout=8)
            self.assertEqual(launcher.returncode, 0, launcher.stderr)
            self.assertIn("offline-ok", launcher.stdout)
            second = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=8)
            self.assertNotEqual(second.returncode, 0)
            self.assertTrue((destination / "xrm742.sh").exists())
            self.assertTrue((bin_dir / "mforce").exists())


if __name__ == "__main__":
    unittest.main()
