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
| `--output`-Dateien | Bleiben am gewählten Speicherort | Anwender |
| Lokale MariaDB (`mforce_logs.module_runs`) | Standardmäßig aus; bei `MF_DB_ENABLE=1` nur Modul-ID, Exit-Code, Zeitstempel; frühere Rohdaten werden beim nächsten aktivierten Start geleert und Metadaten nach 7 Tagen (1–365 konfigurierbar) bereinigt | Anwender; `MF_DB_DISABLE=1` erzwingt Opt-out, manuelle Retention und Backups prüfen |
| Umgeleitete Ausgaben (`>`, `tee`) | Bleiben bis zur manuellen Löschung | Anwender |
| Shell-History | Abhängig von der verwendeten Shell und deren Einstellungen | Anwender |
| Git-Commits / Pull Requests / Issues | Können langfristig erhalten bleiben, auch nach späterem Entfernen | Repository-Betreiber und Plattform |
| DNS-/HTTP-/RDAP-Serverlogs | Außerhalb der Kontrolle des lokalen Programms | Betreiber des jeweiligen Dienstes |
| Backups und Synchronisierung | Können zusätzliche Kopien enthalten | Anwender bzw. beauftragter Dienstleister |

## MariaDB: Kontrolle und manuelle Bereinigung

MForce startet die lokale MariaDB **nur** mit `MF_DB_ENABLE=1` und
vorhandenen `mariadbd`, `mariadb`, `mariadb-install-db`. Die Datenbank
ist nur über Unix-Socket erreichbar. Der persistente Datenordner
liegt unter `${XDG_STATE_HOME:-$HOME/.local/state}/mforce/mariadb/data`.
Ab dieser Version werden keine Modulausgaben gespeichert, nur Modul-ID,
Exit-Code und Zeitstempel. Frühere Rohdaten werden beim nächsten
aktivierten Start geleert, Metadaten nach standardmäßig sieben Tagen
bereinigt (`MF_DB_RETENTION_DAYS=1..365`). Ohne erneuten aktivierten
Start werden Daten nicht automatisch gelöscht.

**Protokollierung bei Bedarf ausdrücklich aktivieren:**

```bash
MF_DB_ENABLE=1 bash xrm742.sh
# Optional: Metadaten 30 Tage aufbewahren
MF_DB_ENABLE=1 MF_DB_RETENTION_DAYS=30 bash xrm742.sh
```

**Protokollierung für eine Sitzung deaktivieren:**

```bash
MF_DB_DISABLE=1 bash xrm742.sh
# Bei Installation mit dem mforce-Launcher:
MF_DB_DISABLE=1 mforce
```

**Alte Datensätze gezielt bereinigen:** Der MariaDB-Server muss
laufen; ggf. MForce in einem anderen Terminal geöffnet halten.
`--days` ist die zuvor intern festgelegte Aufbewahrungsdauer,
hier **nur als Beispiel** 30 Tage.

```bash
bash scripts/mariadb-retention.sh --days 30
# Erst nach Prüfung und Freigabe:
bash scripts/mariadb-retention.sh --days 30 --execute
```

Der erste Aufruf ist ein Dry-Run. Der zweite entfernt ausschließlich
Datenbankzeilen, deren `started_at` älter als die gewählte Zahl
von Tagen ist. Der manuelle Helfer ist **nicht automatisch geplant**. Bei
`MF_DB_ENABLE=1` findet zusätzlich die oben beschriebene Bereinigung
beim Datenbankstart statt. Keine dieser Maßnahmen löscht Backups,
Shell-History oder Exporte. SQL-Löschung garantiert keine physische
Überschreibung des Datenträgers.

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
