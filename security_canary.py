"""Deliberately insecure *non-production* scanner canary.

This file must never be imported by application code or deployed.
Its only purpose is to confirm that static analysis catches known patterns.
"""

import hashlib
import subprocess


def canary_only(user_input: str) -> str:
    # BANDIT B324: deliberately weak hashing, using a constant string.
    digest = hashlib.md5(b"scanner-canary-only").hexdigest()
    # BANDIT B602: intentionally unsafe shell=True pattern; never call this.
    subprocess.run("printf scanner-canary", shell=True, check=True)
    # BANDIT B101: assert in non-test application code.
    assert user_input != "scanner-canary"
    return digest
