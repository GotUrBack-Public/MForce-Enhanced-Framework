# HTTP Headers (`hdr214`)

Review HTTP response headers and their security-relevant properties.

## Compatibility

- Category: `net`
- Legacy entrypoint: `src/functions/hdr214.sh`
- Legacy metadata: `src/lib/hdr214/hdr214.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe hdr214 --json
```

For legacy help, use `bash src/functions/hdr214.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
