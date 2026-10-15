# IP Intelligence (`ipa212`)

Review IP address metadata and network ownership context.

## Compatibility

- Category: `net`
- Legacy entrypoint: `src/functions/ipa212.sh`
- Legacy metadata: `src/lib/ipa212/ipa212.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe ipa212 --json
```

For legacy help, use `bash src/functions/ipa212.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
