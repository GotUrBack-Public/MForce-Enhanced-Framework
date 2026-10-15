"""Check host commands without installing anything."""
import shutil

def inspect():
    return {"required": {x: bool(shutil.which(x)) for x in ("bash", "jq", "python3")},
            "optional": {x: bool(shutil.which(x)) for x in ("git", "shellcheck")}}
