# HTTP Method Auditor (`met405`)

Inspect advertised HTTP methods with an OPTIONS request.

## Compatibility

- Category: `offensive`
- Legacy entrypoint: `src/functions/met405.sh`
- Legacy metadata: `src/lib/met405/met405.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `authorized-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe met405 --json
```

For legacy help, use `bash src/functions/met405.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
