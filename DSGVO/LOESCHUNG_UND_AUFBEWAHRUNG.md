# Aufbewahrung, Export und Löschung

MForce definiert **keine universelle Aufbewahrungsfrist** für
personenbezogene Daten. Die konkrete Frist muss der jeweils
Verantwortliche anhand des Zwecks, der Rechtsgrundlage und
etwaiger gesetzlicher Pflichten festlegen.

## Welche Daten bleiben möglicherweise erhalten?

| Speicherort | Standardverhalten | Verantwortung |
| --- | --- | --- |
| Terminal-Ausgabe | Wird angezeigt, nicht als zentraler MForce-Bericht gespeichert | Anwender; Terminal-Scrollback und Aufzeichnung prüfen |
| Temporäre Sitzungsdatei | Bei regulärem Beenden entfernt; Absturz/SIGKILL kann Reste hinterlassen | Lokale Installation |
| Optionale MariaDB | Standardmäßig deaktiviert. Bei `MF_DB_ENABLE=1` lokale Modul-ID, Exit-Code und Zeitstempel; Aufbewahrung standardmäßig 7 Tage (1–365 konfigurierbar), Bereinigung beim nächsten aktiven Start. Datenbankdateien bleiben sonst bestehen | Anwender; manuelle Löschung und Backups prüfen |
| `--output`-Dateien | Bleiben am gewählten Speicherort | Anwender |
| Umgeleitete Ausgaben (`>`, `tee`) | Bleiben bis zur manuellen Löschung | Anwender |
| Shell-History | Abhängig von der verwendeten Shell und deren Einstellungen | Anwender |
| Git-Commits / Pull Requests / Issues | Können langfristig erhalten bleiben, auch nach späterem Entfernen | Repository-Betreiber und Plattform |
| DNS-/HTTP-/RDAP-Serverlogs | Außerhalb der Kontrolle des lokalen Programms | Betreiber des jeweiligen Dienstes |
| Backups und Synchronisierung | Können zusätzliche Kopien enthalten | Anwender bzw. beauftragter Dienstleister |

## Lokale MariaDB vollständig entfernen

Bei deaktivierter Protokollierung werden vorhandene Daten **nicht** automatisch
bereinigt. Zum Löschen MForce und MariaDB vollständig beenden, den tatsächlichen
Pfad prüfen und das Verzeichnis `$XDG_STATE_HOME/mforce/mariadb` bzw.
`$HOME/.local/state/mforce/mariadb` entfernen. Vorher sicherstellen,
dass keine andere Installation dieses Verzeichnis verwendet. Auch Backups
und Kopien separat prüfen. Bei aktivierter Datenbank entfernt der nächste
Start außerdem alte Roh-Ausgaben aus früheren Versionen und Metadaten,
die älter als `MF_DB_RETENTION_DAYS` sind (Standard: 7 Tage).

## Praktischer Löschablauf

1. Verarbeitung stoppen und erforderliche Nachweise nach Freigabe
   datensparsam sichern.
2. Exportpfade, temporäre Sitzungsreste und manuelle Logdateien
   identifizieren. **Vor jeder Löschung prüfen, dass der Pfad korrekt ist.**
3. Nicht mehr benötigte Dateien mit geeigneten Betriebssystemmitteln
   entfernen; ggf. Papierkorb, Backup und Synchronisationsziele prüfen.
4. Shell-History auf sensible Befehle prüfen. Bei Bedarf Einträge
   gezielt nach der Anleitung der verwendeten Shell bereinigen.
5. Für bereits geteilte Daten (Tickets, Chat, KI-Dienste, GitHub)
   die jeweilige Plattform und deren Löschverfahren verwenden.
6. Löschdatum, Umfang und Ausnahmen intern dokumentieren.

**Hinweis:** Einfaches Löschen garantiert auf Flash-Speichern,
Dateisystem-Snapshots, Backups oder Remote-Diensten keine sichere
physische Vernichtung. Für hohe Schutzbedarfe sind
Datenträgerverschlüsselung, Zugriffskontrolle und geregelte
Medienvernichtung zu prüfen.

## Betroffenenrechte

Anfragen auf Auskunft, Berichtigung, Löschung, Einschränkung,
Datenübertragbarkeit oder Widerspruch müssen vom zuständigen
Verantwortlichen fallbezogen bearbeitet werden. Das Open-Source-Projekt
stellt dafür keine zentrale Nutzer- oder Kundendatenbank und keinen
automatisierten Self-Service-Endpunkt bereit.

## Vorlage für eine interne Löschregel

- Verarbeitung / Zweck: **[eintragen]**
- Datenkategorien: **[eintragen]**
- Speicherorte und Dienstleister: **[eintragen]**
- Rechtsgrundlage: **[eintragen]**
- Aufbewahrungsfrist / Auslöser: **[eintragen]**
- Löschverfahren und Backup-Zyklus: **[eintragen]**
- Verantwortliche Person / Review-Datum: **[eintragen]**

Keine pauschalen Zeitangaben übernehmen, ohne die tatsächliche
Verarbeitung und gesetzliche Anforderungen zu prüfen.
