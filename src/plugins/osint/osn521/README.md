# OSINT Search (`osn521`)

Reserved OSINT search module; currently disabled in the legacy registry.

## Compatibility

- Category: `osint`
- Legacy entrypoint: `src/functions/rpx521.sh`
- Legacy metadata: `src/lib/osn521/osn521.json` (not required while disabled)
- Registry state: **disabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe osn521 --json
```

This entry is intentionally disabled; do not enable it without implementation and tests.
