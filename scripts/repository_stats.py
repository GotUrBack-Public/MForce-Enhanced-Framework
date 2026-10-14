#!/usr/bin/env python3
"""Generate Shields.io endpoint badges from tracked repository files.

Counts are reproducible for the checked-out Git commit:
- files: all tracked regular files and symlinks (not .git or ignored files)
- directories: distinct parent directories of tracked paths (excluding root)
- code lines: non-empty physical lines in tracked source files, including
  comments and tests, for the extensions in CODE_SUFFIXES.
"""
import argparse
import json
import subprocess
from pathlib import Path

CODE_SUFFIXES = frozenset({
    ".sh", ".bash", ".py", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".sql",
})
BADGES = {
    "code-lines.json": ("Code lines", "code_lines", "blue"),
    "files.json": ("Files", "files", "brightgreen"),
    "directories.json": ("Directories", "directories", "orange"),
}


def tracked_paths(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z", "--cached"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [Path(p.decode("utf-8", "surrogateescape"))
            for p in result.stdout.split(b"\0") if p]


def calculate(repo: Path) -> dict[str, int]:
    paths = tracked_paths(repo)
    dirs: set[str] = set()
    lines = 0
    files = 0
    for relative in paths:
        absolute = repo / relative
        if not (absolute.is_file() or absolute.is_symlink()):
            continue
        files += 1
        for parent in relative.parents:
            if str(parent) != ".":
                dirs.add(parent.as_posix())
        if relative.suffix.lower() not in CODE_SUFFIXES or absolute.is_symlink():
            continue
        with absolute.open("rb") as handle:
            lines += sum(bool(line.strip()) for line in handle)
    return {"code_lines": lines, "files": files, "directories": len(dirs)}


def render_badges(counts: dict[str, int]) -> dict[str, str]:
    result = {}
    for filename, (label, key, color) in BADGES.items():
        result[filename] = json.dumps(
            {"schemaVersion": 1, "label": label,
             "message": f"{counts[key]:,}", "color": color},
            ensure_ascii=True, sort_keys=True, separators=(",", ":"),
        ) + "\n"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    counts = calculate(args.repo.resolve())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in render_badges(counts).items():
        (args.output_dir / name).write_text(data, encoding="utf-8")
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
