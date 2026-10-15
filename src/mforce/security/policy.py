"""Built-in module permission classifications."""
def expected(mid, category):
    if mid in ("sys193", "sec601", "xss402"):
        return "local"
    if category == "upd":
        return "maintenance"
    if category == "offensive":
        return "authorized-network"
    return "passive-network"
