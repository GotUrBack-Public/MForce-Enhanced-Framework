# CORS Policy Auditor (`cor404`)

Audit CORS response behavior using two bounded synthetic-origin requests.

## Compatibility

- Category: `offensive`
- Legacy entrypoint: `src/functions/cor404.sh`
- Legacy metadata: `src/lib/cor404/cor404.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `authorized-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe cor404 --json
```

For legacy help, use `bash src/functions/cor404.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
