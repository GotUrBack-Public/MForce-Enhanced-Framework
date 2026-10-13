# Offensive Security: XSS Payload Lab and HTTP Reflection Inspector

**Educational Purpose · Professional Usage · Authorized Targets Only.**

Both modules are functional Python 3 tools that run on Termux and Linux without root access. Neither generates simulated scan results. The payload library is fully offline; the reflection inspector makes actual, bounded HTTP GET requests using harmless alphanumeric markers.

## XSS Payload Lab — `xss402`

100 local example payloads across HTML, attribute, JavaScript string, DOM sink, URL and encoding contexts. The payloads use visible `alert(...)` proof-of-concept markers rather than data exfiltration, stealth or bypass chains. Examples may execute JavaScript **when you deliberately insert them into a vulnerable local lab page**. The tool itself never injects or transmits them.

```bash
bash src/functions/xss402.sh --list-categories
bash src/functions/xss402.sh --category html
bash src/functions/xss402.sh --search innerHTML --format json
bash src/functions/xss402.sh --format lines --output xss-lab.txt
```

The payload list is a reference library, **not** a vulnerability scanner or guarantee of exploitation. A payload working in one context does not imply it will work elsewhere. Contextual encoding and a strict Content Security Policy can prevent execution.

## HTTP Reflection Inspector — `ref403`

Tests at most eight named query parameters in a single run. For each parameter it sends a **unique, harmless alphanumeric marker** and inspects the actual response to identify reflected input in HTML text, HTML attributes, script blocks, comments, or plain text/JSON. It does not send XSS payloads or execute scripts.

```bash
# Run a local test server or your own authorized application first:
bash src/functions/ref403.sh 'http://127.0.0.1:8000/?q=hello' --authorized
bash src/functions/ref403.sh 'http://127.0.0.1:8000/' --authorized --param q --json

# Explicitly authorized public site only:
bash src/functions/ref403.sh 'https://your-authorized-site.example/?q=test' --authorized --allow-public --json
```

Limits: maximum 8 requests per invocation, 256 KiB response body, 0.5–10 second timeout, GET only, no redirect following, stop on HTTP 429, no brute force, no form submissions, no stealth, no authentication. URL parameters can contain sensitive data; the report omits existing query values. A reflected marker **does not establish XSS**.

The `--authorized` flag is a declaration of permission, not a substitute for obtaining it. Public hosts additionally require `--allow-public`. Respect written scope, service terms, data minimization and applicable GDPR/DSGVO obligations. DNS changes between validation and connection are a residual risk; use a controlled network environment for sensitive assessments.

## Test

```bash
python3 -m unittest discover -s tests -v
```
