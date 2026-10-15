# API Metadata (`api312`)

Inspect API metadata without modifying remote resources.

## Compatibility

- Category: `osint`
- Legacy entrypoint: `src/functions/api312.sh`
- Legacy metadata: `src/lib/api312/api312.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe api312 --json
```

For legacy help, use `bash src/functions/api312.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
