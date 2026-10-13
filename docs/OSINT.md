# MForce OSINT Toolkit

**Educational Purpose · Professional Usage · Authorized targets only.**

Ten passive OSINT modules for **Termux and Linux**, available under Network and OSINT in the MForce terminal UI. **Python 3** is required; **dig** is optional for additional DNS record types.

| Category | Modules |
| --- | --- |
| Network | DNS Records; IP Intelligence; TLS Certificate; HTTP Headers |
| OSINT | Website Inspector; API Metadata; Rate Limit Signals; JavaScript DOM Review; Robots & Sitemap; RDAP Registration |

## Run

```bash
# Termux
pkg install python jq
# Debian/Ubuntu
sudo apt install python3 jq

bash xrm742.sh
# Select Network or OSINT

# Direct, authorized public-data checks
bash src/functions/web311.sh https://example.org
bash src/functions/rat313.sh https://example.org
bash src/functions/jsn314.sh https://example.org
bash src/functions/api312.sh https://api.example.org/status
bash src/functions/dns211.sh example.org
bash src/functions/ipa212.sh 1.1.1.1
bash src/functions/tls213.sh example.org
bash src/functions/rob315.sh https://example.org
bash src/functions/rdp316.sh example.org
```

## How to interpret findings

**Rate limits:** An HTTP 429 response means throttling was observed. RateLimit/Retry-After headers indicate advertised limits. No headers means **UNKNOWN**, never “unlimited”. The toolkit never sends bursts, bypasses rate limits, brute-forces or performs load tests.

**JavaScript:** innerHTML, outerHTML, insertAdjacentHTML, document.write, eval, new Function and srcdoc are flagged for manual code review. A match is **not proof of XSS**. The tool does not execute JavaScript or inject payloads. Only inline code and at most three same-origin external scripts are reviewed.

**HTTP:** Missing security headers and cookie attributes are observations, not automatically exploitable vulnerabilities. Public forms are described but never submitted. APIs reveal key names and value types, not sensitive response values.

**Scope and limits:** All HTTP(S) target checks block non-public/private/link-local addresses, use timeouts, bound response sizes and validate redirects. No authentication attempts, crawler, mass IP port scan or credentials. No result files are written automatically. **rdap.org** is an external provider that receives the target on RDAP lookups.

## Educational Purpose / Professional Usage / Datenschutz (DSGVO)

For learning, use systems you own or have permission to inspect. For professional usage, work only within written authorization, contractual scope, service policies and local law.

**DSGVO-konforme Einsatzmöglichkeit** erfordert eine passende Rechtsgrundlage, Zweckbindung, Datenminimierung, Aufbewahrungsfristen und gegebenenfalls eine Prüfung der Drittanbieter-Übermittlung (z. B. RDAP). Personenbezug kann selbst bei öffentlichen IP-Adressen oder URLs bestehen. Es gibt **keine automatische DSGVO-Konformität oder Zertifizierung**. Shell-History, Terminal-Logs und Netzwerk-Provider können Metadaten speichern, auch wenn das Tool selbst Ergebnisse nicht persistiert.
