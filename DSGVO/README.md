# DSGVO / GDPR — Datenschutz und verantwortlicher Einsatz

**Status:** Projektbezogene Dokumentation und ausfüllbare Arbeitshilfen,
Stand 13.10.2026. **Keine verbindliche Datenschutzerklärung, keine
Rechtsberatung und keine DSGVO-Zertifizierung.**

MForce Enhanced Framework ist ein lokal ausführbares Open-Source-Werkzeug
für Termux und Linux. Einige Module stellen echte Netzwerkverbindungen
her. Ob bei einer konkreten Nutzung personenbezogene Daten verarbeitet
werden und welche Pflichten daraus entstehen, hängt vom Einsatzzweck,
den Zielsystemen, den Beteiligten und den verwendeten Dienstleistern ab.

## Dokumente

| Datei | Inhalt |
| --- | --- |
| [DATENFLUESSE.md](DATENFLUESSE.md) | Technische Datenflüsse, externe Kontakte, Risiken |
| [CHECKLISTE.md](CHECKLISTE.md) | Vorbereitungs-, Einsatz- und Review-Checkliste |
| [LOESCHUNG_UND_AUFBEWAHRUNG.md](LOESCHUNG_UND_AUFBEWAHRUNG.md) | Export, Speicherung, Löschung und Fristen |
| [DATENSCHUTZHINWEISE_VORLAGE.md](DATENSCHUTZHINWEISE_VORLAGE.md) | Auszufüllende Vorlage für Betreiberhinweise |
| [VERZEICHNIS_VORLAGE.md](VERZEICHNIS_VORLAGE.md) | Beispiel eines Verarbeitungsverzeichnisses (Art. 30) |
| [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) | Umgang mit Datenschutzvorfällen |

## Kurzüberblick

- **Lokal:** Terminal-Ausgaben, die meisten Laufzeitinformationen und
  eine temporäre Sitzungsdatei werden auf dem eigenen Gerät verarbeitet.
- **Netzwerk:** OSINT, TCP-Scanner und HTTP Reflection Inspector können
  IP-Adressen, Domainnamen, URLs und Anfrage-Metadaten an Zielsysteme
  übermitteln. Das RDAP-Modul kontaktiert `rdap.org`.
- **Website:** Statische GitHub-Pages-Seite ohne im Projekt eingebautes
  Analytics-Skript oder Formular-Backend. GitHub Pages und Browser
  verarbeiten beim Abruf technische Verbindungsdaten; diese Verarbeitung
  liegt nicht vollständig in der Kontrolle des Quellcodes.
- **Dauerhafte Dateien und lokale SQL-Datenbank:** Exporte (`--output`),
  umgeleitete Terminal-Ausgaben, Shell-History, Screenshots, Backups und
  Git-Commits können bestehen bleiben. MariaDB ist standardmäßig aus.
  Siehe [Löschung und Aufbewahrung](LOESCHUNG_UND_AUFBEWAHRUNG.md).
- **MariaDB-Protokollierung:** Nur bei `MF_DB_ENABLE=1` wird lokal
  eine Datenbank gestartet (sofern installiert). Sie speichert nur Modul-ID,
  Exit-Code und Zeitstempel, keine Modulausgaben. Beim nächsten aktivierten
  Start werden frühere Rohdaten geleert und Metadaten älter als sieben Tage
  gelöscht (über `MF_DB_RETENTION_DAYS` auf 1–365 Tage einstellbar).
  `MF_DB_DISABLE=1` erzwingt die Deaktivierung; Backups separat prüfen.
- **Kein automatischer Nachweis:** Die Software stellt weder eine
  Rechtsgrundlage noch eine Einwilligung noch eine Freigabe für Scans bereit.

## Wer ist verantwortlich?

Die datenschutzrechtliche Rolle muss **für den jeweiligen Einsatz**
festgelegt werden. Bei eigenen Prüfungen kann der Anwender Verantwortlicher
sein; bei Kundenaufträgen sind Verantwortlicher, Auftragsverarbeiter und
gegebenenfalls gemeinsame Verantwortlichkeit vertraglich und tatsächlich
zu klären. Die bloße Veröffentlichung dieses Repositories bestimmt die
Rollen nicht.

Für eine veröffentlichte Datenschutzerklärung fehlen derzeit geprüfte
Betreiberangaben (juristischer Name, Kontakt, Hosting-Verträge,
Aufbewahrungsfristen usw.). Bitte keine Platzhalter als echte
Datenschutzhinweise ausgeben. Verwende die [Vorlage](DATENSCHUTZHINWEISE_VORLAGE.md)
erst nach Prüfung und Ergänzung.

## Vor einem produktiven Einsatz

1. Eigentum bzw. schriftliche Scan-Freigabe und genauen Scope prüfen.
2. Zweck und Rechtsgrundlage nach Art. 6 DSGVO bestimmen; bei besonderen
   Datenkategorien zusätzliche Voraussetzungen nach Art. 9 beachten.
3. Daten minimieren, Testdaten bevorzugen und sensible URL-Parameter meiden.
4. Drittanbieter, Hosting, Drittlandübermittlungen und ggf. AV-Verträge
   bewerten (Art. 28, 44 ff.).
5. Aufbewahrung, Löschung, Zugriffsrechte und Betroffenenrechte regeln.
6. Bei hohem Risiko eine Datenschutz-Folgenabschätzung prüfen (Art. 35).
7. Maßnahmen dokumentieren und die Checkliste abzeichnen.

## Grenzen und Geltungsbereich

Diese Dokumentation beschreibt den aktuellen öffentlich sichtbaren
Quellcode, nicht unbekannte Drittanbieter-Logs, GitHub-Betriebsdetails,
Nutzer-Shell-Konfigurationen oder individuelle Deployments. Sie ist
kein Audit und kann ohne erneute Prüfung veralten.

Weitere Richtlinien:
[SECURITY.md](../SECURITY.md) ·
[Guidelines & Terms](../GUIDLINES&&TERMSOFUSE.md) ·
[OSINT](../docs/OSINT.md) ·
[Offensive Security](../docs/OFFENSIVE_XSS.md).
