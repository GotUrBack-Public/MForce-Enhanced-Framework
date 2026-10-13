#!/usr/bin/env python3
"""MForce updater: verified origin, clean working tree, fast-forward only."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = re.compile(r"^(?:https://github\.com/GotUrBack-Public/MForce-Enhanced-Framework(?:\.git)?|git@github\.com:GotUrBack-Public/MForce-Enhanced-Framework(?:\.git)?)$")
CYAN = "\033[96m"
RESET = "\033[0m"


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], text=True, capture_output=True, check=False)


def ensure(condition, message):
    if not condition:
        raise RuntimeError(message)


def progress(title, command):
    """Animated indeterminate progress; never misrepresent network bytes as percent."""
    colored = sys.stdout.isatty() and "NO_COLOR" not in os.environ
    stop = threading.Event()
    frames = ("[=         ]", "[===       ]", "[=====     ]", "[=======   ]", "[========= ]", "[ ======== ]", "[   ====== ]", "[     ==== ]")
    def animate():
        i = 0
        while not stop.wait(0.10):
            frame = frames[i % len(frames)]
            if colored:
                frame = CYAN + frame + RESET
            sys.stdout.write("\r  " + frame + "  " + title + " ...")
            sys.stdout.flush()
            i += 1
    thread = threading.Thread(target=animate, daemon=True)
    thread.start()
    try:
        result = git(*command)
    finally:
        stop.set()
        thread.join()
        sys.stdout.write("\r" + " " * 74 + "\r")
        sys.stdout.flush()
    return result


def run(check_only=False, yes=False):
    ensure(git("--version").returncode == 0, "Git is not installed.")
    ensure(git("rev-parse", "--is-inside-work-tree").stdout.strip() == "true", "Not a Git working tree.")
    ensure(git("rev-parse", "--show-toplevel").stdout.strip() == str(ROOT.resolve()), "Run from the installed MForce repository.")
    remote = git("remote", "get-url", "origin")
    ensure(remote.returncode == 0 and EXPECTED.fullmatch(remote.stdout.strip()), "Origin does not match the official MForce GitHub repository.")
    branch = git("symbolic-ref", "--quiet", "--short", "HEAD")
    ensure(branch.returncode == 0 and branch.stdout.strip() == "main", "Updater supports only the main branch. Switch to main manually.")
    status = git("status", "--porcelain", "--untracked-files=normal")
    ensure(status.returncode == 0 and not status.stdout.strip(), "Local changes detected. Commit or stash them before updating.")
    print("\n  MFORCE / UPDATE CENTER")
    print("  Official source: GotUrBack-Public/MForce-Enhanced-Framework")
    print("  Strategy: verified origin / main / fast-forward only")
    print("  Progress bar shows activity, not a download percentage.\n")
    current = git("rev-parse", "--short", "HEAD").stdout.strip()
    print("  [1/3] Current revision:", current)
    fetch = progress("[2/3] Checking upstream", ["-c", "core.hooksPath=/dev/null", "fetch", "--no-tags", "origin", "main"])
    ensure(fetch.returncode == 0, "Fetch failed: " + fetch.stderr.strip()[-450:])
    target = git("rev-parse", "--short", "FETCH_HEAD").stdout.strip()
    ancestor = git("merge-base", "--is-ancestor", "HEAD", "FETCH_HEAD")
    ensure(ancestor.returncode == 0, "Local branch diverged. Automatic update refused.")
    if current == target:
        print("  [3/3] Already up to date (" + current + ").")
        return 0
    print("  [3/3] Update available:", current, "->", target)
    if check_only:
        print("  Check complete. No files changed.")
        return 0
    if not yes:
        if not sys.stdin.isatty():
            raise RuntimeError("Interactive confirmation required (or pass --yes).")
        answer = input("  Apply official update? [yes/NO] ").strip()
        if answer != "yes":
            print("  Update cancelled.")
            return 0
    result = progress("Applying fast-forward update", ["-c", "core.hooksPath=/dev/null", "merge", "--ff-only", "FETCH_HEAD"])
    ensure(result.returncode == 0, "Update failed: " + result.stderr.strip()[-450:])
    print("  Update complete:", target)
    print("  Restart MForce: bash xrm742.sh")
    return 0


def main():
    parser = argparse.ArgumentParser(description="MForce Update Center — verified fast-forward updates from official GitHub main")
    parser.add_argument("--check", action="store_true", help="Check without changing files")
    parser.add_argument("--yes", action="store_true", help="Confirm update non-interactively")
    args = parser.parse_args()
    try:
        return run(args.check, args.yes)
    except (RuntimeError, OSError) as exc:
        print("  UPDATE ERROR:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
