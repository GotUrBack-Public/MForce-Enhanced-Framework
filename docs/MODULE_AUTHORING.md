# Adding a modular MForce tool

Each tool owns a stable identifier, an independent directory and a documented
compatibility contract. This guide applies while the interactive Bash registry
is still authoritative.

1. Choose a unique ID matching `[a-z]{3}[0-9]{3}` and an existing category.
2. Implement the shell wrapper under `src/functions/` and metadata,
   configuration, help and library under `src/lib/<id>/`.
3. Register the module in `src/data/funcs.json`. Disabled prototypes
   should remain disabled until implementation and tests are complete.
4. Add `src/plugins/<category>/<id>/manifest.json` conforming to
   `src/mforce/contracts/manifest.schema.json`.
5. Add `src/plugins/<category>/<id>/README.md` explaining the purpose,
   safe invocation, authorization requirements and data handling.
6. Add unit tests for normal, invalid and boundary inputs. Avoid external
   network calls in tests; use local fixtures or a mock server.
7. Run `python3 -m src.mforce doctor --json` and
   `python3 -m unittest discover -s tests -v`.

## Compatibility guarantees

- IDs and entrypoints remain stable; renames require an explicit migration.
- No plugin is executed during discovery, validation or catalog display.
- All external active assessments require explicit authorization.
- Keep requests bounded and avoid collecting secrets or personal data.
- Do not add placeholder files just to increase repository statistics.
- Keep README and existing bot runtime unchanged during Phase 1.

## Permission labels

`local`: no remote target. `passive-network`: metadata-oriented remote
requests. `authorized-network`: explicit permission required for target
assessment. `maintenance`: user-initiated update operations. These are
descriptive classifications; the implementation must enforce safety.
