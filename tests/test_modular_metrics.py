"""File and folder milestone counts must be deterministic."""
from pathlib import Path
import tempfile
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


if __name__ == "__main__":
    unittest.main()
