# MForce Security Tools V2 — 1 defensive + 4 offensive

These five modules are implemented using Python 3's standard library and
integrated with the existing MForce registry, module preview and help system.
No third-party Python packages are required. They are not exploit frameworks.

## Defensive Security

**sec601 — Local Secret Scanner:** scans a local file or directory offline,
up to 250 regular files of at most 1 MiB each. Reports possible private-key
markers, GitHub token patterns, AWS access-key identifiers and generic
credential assignments. Output contains only relative file paths, line
numbers and rule IDs, **never secret values**. Returns exit code 1 when
potential findings are present. Patterns can generate false positives;
manual validation is necessary. Symlinks and common dependency/cache folders
are skipped.

```bash
bash src/functions/sec601.sh ./my-project --json
```

## Offensive Security (authorized targets only)

Every active module requires `--authorized`. Public destinations additionally
require `--allow-public`. DNS addresses are validated before connections and
the chosen destination IP is pinned. HTTP redirects are not followed, HTTP 429
stops checks, and requests have a bounded timeout (default 4 seconds).
No credentials or authentication headers are sent.

| ID | Module | Actual behavior | Limit |
| --- | --- | --- | --- |
| `cor404` | CORS Policy Auditor | Two GETs with harmless distinct Origin headers | 2 requests |
| `met405` | HTTP Method Auditor | Reads OPTIONS / Allow headers; no PUT/DELETE requests | 1 request |
| `coo406` | Cookie Flag Auditor | Reviews Secure, HttpOnly and SameSite without printing cookie names/values | 1 GET |
| `pth407` | Exposure Path Auditor | HEAD-only checks for five fixed potentially sensitive paths | 5 HEADs |

```bash
bash src/functions/cor404.sh http://127.0.0.1:8000 --authorized --json
bash src/functions/met405.sh http://127.0.0.1:8000 --authorized --json
bash src/functions/coo406.sh http://127.0.0.1:8000 --authorized --json
bash src/functions/pth407.sh http://127.0.0.1:8000 --authorized --json
```

A reflected CORS origin, a permissive method header, missing cookie flags or
an HTTP 200 response from a sensitive path is a **review signal**, not proof
of a vulnerability. The path auditor never downloads sensitive file contents.
Checks can still appear in target web server logs; ensure written authorization,
a defined scope, suitable privacy/legal basis and an approved test window.

## Limitations

- A single GET or HEAD cannot validate full application security.
- HTTP status 200 may be a generic fallback; false positives are possible.
- The CORS checker uses two synthetic, non-existent origin hostnames; it
  does not attempt browser exploitation.
- HTTP GET is assumed to be safe; poorly designed endpoints may have side
  effects even for GET/HEAD. Prefer a test environment.
- Local secret scanning does not replace dedicated secret-management tools.
- Results are printed locally and are not automatically uploaded.
- `--json` enables structured output; handle any exported results responsibly.
