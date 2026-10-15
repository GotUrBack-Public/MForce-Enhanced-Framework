"""Human-readable, non-ANSI diagnostics."""
def doctor_report(data):
    lines = [f"MForce modular doctor: {'OK' if data['ok'] else 'FAILED'} "
             f"({data['checked_modules']} manifests)"]
    for issue in data["issues"]:
        lines.append(f"[{issue['severity']}] {issue['code']} {issue['path']}: {issue['message']}")
    if data["runtime"]:
        for kind, commands in data["runtime"].items():
            lines.append(kind + ": " + ", ".join(
                f"{name}={'found' if present else 'missing'}"
                for name, present in commands.items()))
    return "\n".join(lines)
