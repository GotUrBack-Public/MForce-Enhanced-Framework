# Local Secret Scanner (`sec601`)

Scan local files for possible credential patterns without revealing secret values.

## Compatibility

- Category: `defensive`
- Legacy entrypoint: `src/functions/sec601.sh`
- Legacy metadata: `src/lib/sec601/sec601.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `local`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe sec601 --json
```

For legacy help, use `bash src/functions/sec601.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
