# Rate Limit Signals (`rat313`)

Report observed rate-limit signals in HTTP responses.

## Compatibility

- Category: `osint`
- Legacy entrypoint: `src/functions/rat313.sh`
- Legacy metadata: `src/lib/rat313/rat313.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe rat313 --json
```

For legacy help, use `bash src/functions/rat313.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
