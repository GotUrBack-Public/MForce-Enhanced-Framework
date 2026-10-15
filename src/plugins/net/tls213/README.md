# TLS Certificate (`tls213`)

Inspect public TLS certificate information.

## Compatibility

- Category: `net`
- Legacy entrypoint: `src/functions/tls213.sh`
- Legacy metadata: `src/lib/tls213/tls213.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe tls213 --json
```

For legacy help, use `bash src/functions/tls213.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
