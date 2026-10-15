# Exposure Path Auditor (`pth407`)

Inspect five fixed exposure paths using HEAD requests only.

## Compatibility

- Category: `offensive`
- Legacy entrypoint: `src/functions/pth407.sh`
- Legacy metadata: `src/lib/pth407/pth407.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `authorized-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe pth407 --json
```

For legacy help, use `bash src/functions/pth407.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
