# Cookie Flag Auditor (`coo406`)

Review cookie security attributes without exposing cookie names or values.

## Compatibility

- Category: `offensive`
- Legacy entrypoint: `src/functions/coo406.sh`
- Legacy metadata: `src/lib/coo406/coo406.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `authorized-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe coo406 --json
```

For legacy help, use `bash src/functions/coo406.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
