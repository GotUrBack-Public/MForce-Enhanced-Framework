"""File and folder milestone counts must be deterministic."""
from pathlib import Path
import tempfile
import subprocess
import unittest

from src.mforce.metrics.counts import measure


class ModularMetricsTests(unittest.TestCase):
    def test_archive_fallback_and_folder_count(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "one/two").mkdir(parents=True)
            (root / "one/two/file.py").write_text("print('hello')")
            (root / "one/other.txt").write_text("hi")
            (root / ".git").mkdir()
            (root / ".git/config").write_text("not a project")
            data = measure(root)
            self.assertEqual(data["files"], 2)
            self.assertEqual(data["directories"], 2)
            self.assertEqual(data["source"], "filesystem")
            self.assertEqual(data["remaining"]["files"], 498)
            self.assertEqual(data["remaining"]["directories"], 148)

    def test_progress_is_capped(self):
        with tempfile.TemporaryDirectory() as temp:
            data = measure(Path(temp))
            self.assertEqual(data["progress_percent"]["files"], 0)
            self.assertEqual(data["progress_percent"]["directories"], 0)

    def test_nested_archive_does_not_use_parent_git_index(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            subprocess.run(["git", "init", "-q", str(parent)], check=True, timeout=10)
            (parent / "parent.txt").write_text("parent", encoding="utf-8")
            subprocess.run(["git", "-C", str(parent), "add", "parent.txt"],
                           check=True, timeout=10)
            root = parent / "archive"
            (root / ".git").mkdir(parents=True)
            (root / "local.txt").write_text("archive", encoding="utf-8")
            data = measure(root)
            self.assertEqual(data["source"], "filesystem")
            self.assertEqual(data["files"], 1)
            self.assertEqual(data["directories"], 0)

    def test_valid_git_checkout_ignores_untracked_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            subprocess.run(["git", "init", "-q", str(root)], check=True, timeout=10)
            for name in ("tracked.txt", "untracked.txt"):
                (root / name).write_text(name, encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.txt"],
                           check=True, timeout=10)
            data = measure(root)
            self.assertEqual(data["source"], "git")
            self.assertEqual(data["files"], 1)


if __name__ == "__main__":
    unittest.main()
