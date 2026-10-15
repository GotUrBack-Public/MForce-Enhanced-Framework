"""Count tracked files and their parent directories, with archive fallback."""
import os
from pathlib import Path
import subprocess

IGNORED = {".git", "__pycache__", ".venv", "venv", "node_modules", ".tox"}
GOALS = {"files": 500, "directories": 150}


def tracked(root):
    root = Path(root).resolve()
    if (root / ".git").exists():
        try:
            process = subprocess.run(["git", "-C", str(root), "ls-files", "--cached", "-z"],
                                     check=True, capture_output=True, timeout=8)
            return ([Path(x.decode("utf-8", "surrogateescape"))
                     for x in process.stdout.split(b"\0") if x], "git")
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
    files = []
    for directory, folders, filenames in os.walk(root, followlinks=False):
        folders[:] = sorted(x for x in folders if x not in IGNORED)
        for name in sorted(filenames):
            p = Path(directory) / name
            if p.is_file() or p.is_symlink():
                files.append(p.relative_to(root))
    return files, "filesystem"


def measure(root):
    root = Path(root).resolve()
    paths, source = tracked(root)
    paths = [p for p in paths if (root / p).is_file() or (root / p).is_symlink()]
    dirs = {parent.as_posix() for path in paths for parent in path.parents
            if parent.as_posix() != "."}
    counts = {"files": len(paths), "directories": len(dirs)}
    return {**counts, "source": source, "goals": GOALS,
            "remaining": {k: max(0, v - counts[k]) for k, v in GOALS.items()},
            "progress_percent": {k: round(min(100, counts[k] * 100 / v), 1)
                                 for k, v in GOALS.items()}}
