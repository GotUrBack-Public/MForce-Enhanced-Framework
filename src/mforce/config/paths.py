"""Path resolution independent of the invoking working directory."""
from pathlib import Path

def root():
    return Path(__file__).resolve().parents[3]
