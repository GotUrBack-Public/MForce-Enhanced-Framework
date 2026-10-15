"""Filter catalog data without invoking modules."""
def select(modules, category=None, enabled_only=False):
    return [m for m in modules if (category is None or m["category"] == category)
            and (not enabled_only or m["enabled"])]
