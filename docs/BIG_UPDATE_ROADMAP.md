# Big Update — modularity and capability roadmap

**Planning date:** 15 October 2026. **Target date:** Sunday, 18 October 2026.

Starting point on `main`: **226 tracked files**, **59 parent directories**,
**23 registered modules**, **21 enabled**.

Targets: **at least 500 useful tracked files** and **150 meaningful folders**.
These are milestones, not a reason to generate filler or compromise tests.

| Milestone | Target files | Target folders | Deliverable |
| --- | ---: | ---: | --- |
| Phase 1: modular foundation | ~310 | ~100 | Per-module manifests, catalog, doctor, metrics, CI |
| Phase 2: shared services | 380 | 120 | Typed outputs, input validation, platform adapters, fixtures |
| Phase 3: extension ecosystem | 450 | 140 | Contract tests, module templates, capability registry, test matrix |
| Phase 4: hardening and release | 500+ | 150+ | Migration tests, packaging verification, accessibility, documentation |

The targets after Phase 1 are **planned**, not implemented. Work must be
verified on CI before it is considered complete. Growth is measured from
tracked files and their parent directories; empty directories do not count.

## Quality gates

- Existing interactive CLI and all 21 enabled modules keep working.
- Registry/manifests and per-module metadata must agree.
- No breaking changes to user config, install paths, bot logic or README.
- Every new module or adapter needs behavior-focused tests.
- Security assessments retain authorization, rate and privacy safeguards.
- GitHub Packages and release workflows remain operational.
- Counts are published by the existing repository-statistics workflow.

Run `python3 -m src.mforce stats --json` to see the current count and
remaining gap; the result uses `git ls-files` when a checkout is available.
