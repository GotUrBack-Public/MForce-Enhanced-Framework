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
| Lokale MariaDB (`mforce_logs.module_runs`) | Speichert bei verfügbarer MariaDB bis zu 1 MiB Roh-Modulausgabe pro Aufruf dauerhaft; **keine automatische Löschung** | Anwender; Opt-out über `MF_DB_DISABLE=1`, manuelle Retention nach Freigabe |
| Umgeleitete Ausgaben (`>`, `tee`) | Bleiben bis zur manuellen Löschung | Anwender |
| Shell-History | Abhängig von der verwendeten Shell und deren Einstellungen | Anwender |
| Git-Commits / Pull Requests / Issues | Können langfristig erhalten bleiben, auch nach späterem Entfernen | Repository-Betreiber und Plattform |
| DNS-/HTTP-/RDAP-Serverlogs | Außerhalb der Kontrolle des lokalen Programms | Betreiber des jeweiligen Dienstes |
| Backups und Synchronisierung | Können zusätzliche Kopien enthalten | Anwender bzw. beauftragter Dienstleister |

## MariaDB: Kontrolle und manuelle Bereinigung

Wenn `mariadbd`, `mariadb` und `mariadb-install-db` verfügbar
sind, startet MForce normalerweise einen lokalen, ausschließlich über
Unix-Socket erreichbaren MariaDB-Server. Der persistente Datenordner
liegt unter `${XDG_STATE_HOME:-$HOME/.local/state}/mforce/mariadb/data`.
Datenbank und Modulausgaben bleiben nach Programmende erhalten.

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
von Tagen ist. Die Funktion ist **nicht automatisch geplant** und
löscht keine Backups, Shell-History oder exportierten Dateien.
SQL-Löschung garantiert keine physische Überschreibung des
Datenträgers. Für datenschutzkritische Nutzung ist der Opt-out
vorzuziehen, bis eine geprüfte Minimierungs- und Löschstrategie
in der eigentlichen Laufzeit implementiert wurde.

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
