# HTTP Reflection Inspector (`ref403`)

Inspect HTTP reflection behavior on explicitly authorized targets.

## Compatibility

- Category: `offensive`
- Legacy entrypoint: `src/functions/ref403.sh`
- Legacy metadata: `src/lib/ref403/ref403.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `authorized-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe ref403 --json
```

For legacy help, use `bash src/functions/ref403.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
