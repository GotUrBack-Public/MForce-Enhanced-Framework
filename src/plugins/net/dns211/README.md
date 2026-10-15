# DNS Records (`dns211`)

Inspect DNS records for a specified domain.

## Compatibility

- Category: `net`
- Legacy entrypoint: `src/functions/dns211.sh`
- Legacy metadata: `src/lib/dns211/dns211.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe dns211 --json
```

For legacy help, use `bash src/functions/dns211.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
