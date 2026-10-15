# Update MForce (`upd501`)

Run the existing MForce update workflow.

## Compatibility

- Category: `upd`
- Legacy entrypoint: `src/functions/upd501.sh`
- Legacy metadata: `src/lib/upd501/upd501.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `maintenance`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe upd501 --json
```

For legacy help, use `bash src/functions/upd501.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
