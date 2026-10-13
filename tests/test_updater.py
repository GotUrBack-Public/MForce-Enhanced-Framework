import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace

PATH = Path(__file__).resolve().parents[1] / "src/update/updater.py"
spec = importlib.util.spec_from_file_location("mforce_updater", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def response(out="", rc=0, err=""):
    return SimpleNamespace(stdout=out, returncode=rc, stderr=err)


class UpdaterTests(unittest.TestCase):
    def test_official_remote(self):
        self.assertTrue(mod.EXPECTED.fullmatch("https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git"))
        self.assertTrue(mod.EXPECTED.fullmatch("git@github.com:GotUrBack-Public/MForce-Enhanced-Framework.git"))
        self.assertFalse(mod.EXPECTED.fullmatch("https://github.com/attacker/MForce-Enhanced-Framework.git"))

    @patch.object(mod, "progress")
    @patch.object(mod, "git")
    def test_check_never_merges(self, git, progress):
        def fake(*args):
            key = " ".join(args)
            if "--is-inside-work-tree" in key: return response("true\n")
            if "--show-toplevel" in key: return response(str(mod.ROOT.resolve())+"\n")
            if "get-url" in key: return response("https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git\n")
            if "symbolic-ref" in key: return response("main\n")
            if "status" in key: return response("")
            if "rev-parse" in key: return response("abc123\n" if "HEAD" == args[-1] else "def456\n")
            return response()
        git.side_effect = fake
        progress.return_value = response()
        self.assertEqual(mod.run(check_only=True), 0)
        self.assertEqual(progress.call_count, 1)

    @patch.object(mod, "git")
    def test_dirty_tree_refused(self, git):
        def fake(*args):
            key = " ".join(args)
            if "--is-inside-work-tree" in key: return response("true\n")
            if "--show-toplevel" in key: return response(str(mod.ROOT.resolve())+"\n")
            if "get-url" in key: return response("https://github.com/GotUrBack-Public/MForce-Enhanced-Framework.git\n")
            if "symbolic-ref" in key: return response("main\n")
            if "status" in key: return response(" M file.txt\n")
            return response()
        git.side_effect = fake
        with self.assertRaisesRegex(RuntimeError, "Local changes"):
            mod.run(check_only=True)


if __name__ == "__main__":
    unittest.main()
