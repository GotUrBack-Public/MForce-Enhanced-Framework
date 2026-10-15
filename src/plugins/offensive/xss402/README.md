# XSS Payload Lab (`xss402`)

Generate and inspect local XSS test payloads without targeting live services.

## Compatibility

- Category: `offensive`
- Legacy entrypoint: `src/functions/xss402.sh`
- Legacy metadata: `src/lib/xss402/xss402.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `local`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe xss402 --json
```

For legacy help, use `bash src/functions/xss402.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
