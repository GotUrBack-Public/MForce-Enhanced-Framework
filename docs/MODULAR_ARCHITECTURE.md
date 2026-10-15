# MForce modular architecture — Phase 1

The existing interactive Bash runtime, entrypoints and public tool registry
remain unchanged. This phase adds a **read-only, manifest-based discovery
layer** under `src/plugins/` and a dependency-free Python developer CLI.

## Layout

| Path | Responsibility |
| --- | --- |
| `src/plugins/<category>/<id>/manifest.json` | Independently discoverable module descriptor |
| `src/plugins/<category>/<id>/README.md` | Module-specific contract and safety notes |
| `src/mforce/catalog/` | Strict JSON parsing, discovery, filtering |
| `src/mforce/contracts/` | Versioned manifest schema |
| `src/mforce/compat/` | Existing shell wrapper and metadata layout |
| `src/mforce/diagnostics/` | Drift, missing files and duplicate-ID detection |
| `src/mforce/security/` | Declarative risk/permission labels |
| `src/mforce/platform/` | Optional runtime dependency diagnostics |
| `src/mforce/metrics/` | Reproducible file/folder milestone tracking |
| `src/mforce/reports/` | Human-readable diagnostics |
| `src/mforce/config/` | Repository-root resolution |

All plugin discovery is **read-only**: no imports from tool implementations,
no shell execution, no network requests, no telemetry. The `permission`
field documents the intended usage context but **does not authorize** active
security checks or replace their runtime permission gates.

## Developer commands

```bash
python3 -m src.mforce doctor
python3 -m src.mforce doctor --json --runtime
python3 -m src.mforce catalog --enabled-only
python3 -m src.mforce catalog --category offensive --json
python3 -m src.mforce describe sec601 --json
python3 -m src.mforce stats --json
```

The CLI accepts `--root PATH` before the subcommand for isolated test
fixtures. The `doctor` command exits nonzero for integrity errors. Missing
host dependencies are warnings when `--runtime` is requested.

## Migration strategy

1. Phase 1: register all 23 existing modules in per-module manifests and
   validate them against the unchanged `src/data/funcs.json`.
2. Phase 2: extract shared helpers into testable, platform-specific adapters
   while retaining Bash wrappers and behavior.
3. Phase 3: add contract-tested extension points, independent module tests
   and common output formats.
4. Phase 4: gradually opt modules into the new interfaces with backward
   compatibility and documented deprecation policy.

The old registry is still authoritative for the interactive menu. **Do not**
treat adding a manifest alone as enabling a new tool. Both layers must agree,
and the module must provide its actual implementation and tests.
