# Technische Datenflüsse und Drittanbieter

**Stand:** 13.10.2026. Diese Übersicht ist eine technische
Bestandsaufnahme auf Basis des Repository-Codes, keine rechtliche
Bewertung einzelner Einsätze.

## Übersicht

| Funktion / Quelle | Mögliche Daten | Empfänger / Speicherort | Hinweise |
| --- | --- | --- | --- |
| Terminal-UI / Systeminformationen | Hostname, Interface-Adressen, OS-/Geräteinformationen | Lokales Terminal | Keine zentrale MForce-Uploadfunktion; Screenshots und History separat betrachten |
| Sitzungsverwaltung (`src/auth/sns.sh`) | Sitzungskennung, Erstellungszeit, lokales Flag | Privates temporäres Verzeichnis | Wird bei normalem Ende / behandelten Signalen entfernt; nicht garantiert nach SIGKILL oder Stromausfall |
| DNS-/IP-/TLS-Modi | Domain/IP, DNS-Anfragen, TLS-Verbindungsdaten | Resolver, Zielhost, Netzwerkprovider | DNS- und Netzwerkmetadaten können extern protokolliert werden |
| Website-, HTTP-, API-, Rate- und JS-Modi | Ziel-URL, Pfad, Anfrageheader, Quelltext bis zu Modulgrenzen | Angefragter Webserver, lokale Ausgabe | GET-Anfragen können serverseitige Logs erzeugen; keine versteckten Scans |
| Robots / Sitemap | Zielhost, angefragte Dokumente | Zielhost, lokale Ausgabe | Dokumente werden gelesen, verlinkte Pfade nicht automatisch durchlaufen |
| RDAP | Abgefragte Domain/IP | `rdap.org` und ggf. Registry-Weiterleitung | Drittanbieter erhält die Zielangabe und Verbindungsmetadaten |
| TCP Port Scanner | Ziel-IP/Host, Ports, Verbindungsversuche | Zielsystem und dessen Netzwerklogs | Aktive TCP-Verbindungen, ausdrücklich nur mit Freigabe |
| HTTP Reflection Inspector | URL, vorhandene Query-Werte, harmlose Testmarker | Autorisierter Webserver | Bis zu acht GET-Anfragen; URL-Query kann sensible Daten enthalten; Bericht blendet ursprüngliche Query-Werte aus |
| XSS Payload Lab | Beispielpayloads, Suchbegriffe | Lokal | Keine Netzwerkübertragung durch das Modul; Export auf Wunsch |
| Update Center | Git-Repository-Adresse, Fetch-Metadaten | GitHub / lokale Git-Objekte | Offizieller `main`-Branch, nur Fast-Forward |
| Statische Website | IP-Adresse, Browser-/Verbindungsmetadaten beim Abruf | GitHub Pages und ggf. Netzbetreiber | Keine eigene Analytics-Integration im Projektcode; Hosting-Logs außerhalb des Repositorys |
| GitHub-Links / README-Badges | Browser-/Request-Metadaten | GitHub, `img.shields.io` beim Badge-Abruf | Externe Ressourcen sind gesondert zu berücksichtigen |
| Manuelle Exporte / Screenshots | Scanergebnisse, URLs, IPs, ggf. personenbezogene Angaben | Vom Nutzer gewähltes Dateisystem, Backups oder geteilte Dienste | Nutzer verwaltet Zugriff, Speicherfrist und Löschung |

## Technische Schutzmaßnahmen im aktuellen Code

- OSINT-Anfragen haben Größen- und Timeout-Grenzen; die meisten Modi
  blockieren lokale und nicht öffentliche Zieladressen.
- Der Reflection Inspector erfordert `--authorized` und für öffentliche
  Hosts zusätzlich `--allow-public`. Er folgt Redirects nicht, stoppt
  bei HTTP 429 und sendet keine XSS-Payloads.
- Der TCP Scanner begrenzt Ports, Worker und Zeitlimits.
- Die XSS-Beispielbibliothek arbeitet offline.
- Die Update-Funktion prüft den offiziellen Remote und den sauberen
  Git-Arbeitsbaum; sie lädt Updates von GitHub.
- Temporäre Sitzungsdateien verwenden restriktive Dateirechte und
  werden bei regulärem Ende entfernt.

## Nicht abgedeckte Risiken

- **DNS-Rebinding / TOCTOU:** Hostnamen können zwischen Auflösung und
  Verbindungsaufbau wechseln. Sicherheitsprüfungen sind keine
  Garantie für eine unveränderliche Zieladresse.
- **Drittanbieter-Logs:** Zielserver, DNS-Resolver, Mobilfunkprovider,
  GitHub und RDAP-Betreiber können Metadaten speichern.
- **Shell-History:** Befehle mit sensiblen URLs oder Parametern können
  in der Shell-History landen.
- **Unbeabsichtigte Datenweitergabe:** Terminal-Logs, Screenshots,
  Issues, Pull Requests, Exporte und KI-Dienste können Daten offenlegen.
- **Kein zentraler Löschknopf:** MForce kann fremde Serverlogs,
  Git-History, Backups oder Nutzerdateien nicht vollständig entfernen.

## Prüfpunkte bei Codeänderungen

Neue externe Endpunkte, Tracking-Skripte, Formulare, Datenspeicher,
Exports, APIs oder automatische Uploads müssen hier dokumentiert
und in der Datenschutz-Checkliste bewertet werden. Insbesondere
bei Änderungen an `src/osint/`, `src/offensive/`, `src/update/`,
`src/auth/` oder `web/` ist ein Privacy-Review erforderlich.

**Wichtig:** Diese Tabelle beschreibt technische Möglichkeiten, nicht
automatisch die Zwecke, Rechtsgrundlagen oder Verantwortlichkeiten
eines konkreten Verantwortlichen.
