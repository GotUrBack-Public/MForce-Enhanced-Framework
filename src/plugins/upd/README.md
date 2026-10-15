# upd plugin family

Maintenance and update operations. Changes must be explicitly initiated by the operator.

Each module is independently documented under its own directory. Discovery reads only `manifest.json`; it does not execute shell scripts or issue network requests. The legacy `src/data/funcs.json` registry remains the source of truth for the interactive interface during the compatibility phase.
