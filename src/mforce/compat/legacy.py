"""Legacy metadata and entrypoint paths."""
from pathlib import Path

def paths(root, module):
    mid = module["id"]
    base = Path(root) / "src/lib" / mid
    return {
        "wrapper": Path(root) / "src/functions" / module["entry"],
        "metadata": base / f"{mid}.json",
        "config": base / f"{mid}.conf",
        "help": base / f"{mid}.help",
    }
