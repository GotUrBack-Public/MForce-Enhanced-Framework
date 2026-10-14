# DSGVO-Checkliste für einen konkreten Einsatz

> Arbeitsvorlage. Ohne Prüfung durch den jeweiligen Verantwortlichen
> kein Nachweis einer vollständigen DSGVO-Konformität.

## A. Vor dem Einsatz

- [ ] Zweck, Projekt, Ansprechpartner und Geltungsbereich dokumentiert.
- [ ] Eigentum oder **schriftliche Autorisierung** für alle Zielsysteme liegt vor.
- [ ] Datenkategorien einschließlich IP-Adressen, URL-Parametern,
      Nutzernamen und möglichen Personenbezügen identifiziert.
- [ ] Rechtsgrundlage nach Art. 6 DSGVO je Verarbeitung dokumentiert.
- [ ] Besondere Kategorien nach Art. 9 DSGVO ausgeschlossen oder
      gesondert rechtlich geprüft.
- [ ] Rollen (Verantwortlicher, Auftragsverarbeiter, ggf. gemeinsame
      Verantwortliche) geklärt; ggf. AV-Vertrag nach Art. 28 geprüft.
- [ ] Transparenzpflichten / Datenschutzhinweise nach Art. 13/14 geprüft.
- [ ] Datenminimierung und Zweckbindung (Art. 5) sichergestellt.
- [ ] Technische und organisatorische Maßnahmen (Art. 32) festgelegt.
- [ ] Notwendigkeit einer Datenschutz-Folgenabschätzung (Art. 35) geprüft.
- [ ] Empfänger, Hosting, RDAP, DNS, GitHub und Drittlandtransfers
      einschließlich Art. 44 ff. bewertet.
- [ ] Löschfristen und Verantwortliche für die Löschung festgelegt.
- [ ] Lokale MariaDB ist standardmäßig aus. Falls ausdrücklich mit
      `MF_DB_ENABLE=1` aktiviert: Speicherort, Berechtigungen, Retention,
      manuelle Löschung und Backups prüfen. `MF_DB_DISABLE=1` erzwingt Opt-out.

## B. Während des Einsatzes

- [ ] Nur die ausdrücklich freigegebenen Hosts, Pfade, Ports und
      Zeitfenster verwenden.
- [ ] Testdaten oder anonymisierte Daten bevorzugen.
- [ ] Keine Zugangsdaten oder personenbezogenen Query-Werte in
      Shell-History, Tickets oder Screenshots veröffentlichen.
- [ ] Ergebnisdaten auf das notwendige Minimum beschränken.
- [ ] Ratenlimits und Betriebsrisiken beachten; keine Umgehung.
- [ ] Exporte verschlüsselt bzw. mit passenden Zugriffsrechten speichern.
- [ ] Auffälligkeiten und mögliche Datenschutzvorfälle dokumentieren.

## C. Nach dem Einsatz

- [ ] Berichte auf Erforderlichkeit, Geheimnisse und personenbezogene
      Inhalte prüfen und ggf. schwärzen.
- [ ] Nicht benötigte Rohdaten, Exporte und temporäre Dateien löschen.
- [ ] Shell-History, Backups, CI-Artefakte und externe Plattformen
      gesondert prüfen.
- [ ] Festgelegte Aufbewahrungsfristen dokumentieren und einhalten.
- [ ] Betroffenenanfragen und Meldepflichten in den Prozess aufnehmen.
- [ ] Änderungen an Datenflüssen / Verarbeitungsverzeichnis nachtragen.
- [ ] Projektabschluss und Verantwortliche festhalten.

## D. Interne Freigabe (ausfüllen)

| Feld | Eintrag |
| --- | --- |
| Verantwortliche Organisation | **[eintragen]** |
| Projekt / Verarbeitung | **[eintragen]** |
| Datum / Version | **[eintragen]** |
| Zweck und Rechtsgrundlage | **[eintragen]** |
| Genehmigter Ziel-Scope | **[eintragen]** |
| Aufbewahrungsfrist | **[eintragen]** |
| Drittanbieter / Übermittlungen | **[eintragen]** |
| Verantwortliche Person | **[eintragen]** |
| Review / Freigabe | **[eintragen]** |

Diese Checkliste ist keine juristische Prüfung und ersetzt weder
das Verzeichnis nach Art. 30 noch eine ggf. erforderliche DSFA.
