# Robots & Sitemap (`rob315`)

Inspect robots.txt and sitemap discovery metadata.

## Compatibility

- Category: `osint`
- Legacy entrypoint: `src/functions/rob315.sh`
- Legacy metadata: `src/lib/rob315/rob315.json` (present and verified by doctor)
- Registry state: **enabled**
- Permission classification: `passive-network`

The manifest is **declarative** and does not grant authorization or bypass existing runtime checks. Discovery never executes the module. The original Bash module remains the implementation and is unchanged by this phase.

## Read-only inspection

```bash
python3 -m src.mforce describe rob315 --json
```

For legacy help, use `bash src/functions/rob315.sh --help`. Only run active checks on systems you own or have explicit permission to assess.
