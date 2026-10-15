# Website Inspector (`web311`)

Inspect publicly accessible website metadata.

## Compatibility

- Category: `osint`
- Legacy entrypoint: `src/functions/web311.sh`
- Legacy metadata: `src/lib/web311/web311.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe web311 --json
```

For legacy help, use `bash src/functions/web311.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
