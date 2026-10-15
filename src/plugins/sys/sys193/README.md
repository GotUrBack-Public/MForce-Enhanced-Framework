# System Information (`sys193`)

Report local system environment and platform information.

## Compatibility

- Category: `sys`
- Legacy entrypoint: `src/functions/vkn193.sh`
- Legacy metadata: `src/lib/sys193/sys193.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `local`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe sys193 --json
```

For legacy help, use `bash src/functions/vkn193.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
