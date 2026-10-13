# Datenschutzvorfälle — interner Ablaufplan

**Vorlage für Anwender und Betreiber.** Kein 24/7-Meldedienst und
keine Zusage, dass das MForce-Projekt selbst Verantwortlicher
für fremde Installationen ist.

## 1. Erkennen und eindämmen

Mögliche Auslöser: versehentlich veröffentlichte Scanlogs,
persönliche URL-Parameter in Issues, offengelegte API-Schlüssel,
unautorisierte Exporte, Verlust eines unverschlüsselten Geräts
oder Weitergabe an einen ungeprüften Drittanbieter.

- Zugriff auf betroffene Systeme und Dateien begrenzen.
- Bei aktiver Offenlegung weitere Verteilung stoppen.
- Keine Daten oder Logs in öffentlichen Issues nachreichen.
- Beweise und Zeitpunkte minimal und sicher dokumentieren.
- Schlüssel und Zugangsdaten bei Bedarf nach gesichertem
  Verfahren rotieren.

## 2. Zuständigkeit klären

Feststellen, wer datenschutzrechtlich Verantwortlicher,
Auftragsverarbeiter und ggf. Kunde ist. Die zuständige interne
Kontaktstelle, Auftragsverarbeitungsverträge und
Benachrichtigungswege heranziehen.

## 3. Risiko bewerten

Welche personenbezogenen Daten, wie viele Personen,
welche Empfänger, welche Schutzmaßnahmen und welche Folgen
sind betroffen? Liegt eine Verletzung des Schutzes
personenbezogener Daten nach Art. 4 Nr. 12 DSGVO vor?

## 4. Meldungen prüfen

- Bei einer meldepflichtigen Verletzung ist die zuständige
  Aufsichtsbehörde grundsätzlich **unverzüglich und möglichst
  binnen 72 Stunden nach Bekanntwerden** zu informieren
  (Art. 33 DSGVO); Ausnahmen und Begründungen sind zu prüfen.
- Bei voraussichtlich hohem Risiko sind ggf. betroffene
  Personen nach Art. 34 DSGVO zu benachrichtigen.
- Auftragsverarbeiter informieren den Verantwortlichen
  nach den gesetzlichen und vertraglichen Vorgaben.
- Auch nicht meldepflichtige Vorfälle sind nach den
  geltenden Dokumentationspflichten zu erfassen.

Die 72-Stunden-Regel ist **keine allgemeine Frist für jeden
Softwarefehler**; maßgeblich sind Art und Bewertung des Vorfalls.

## 5. Wiederherstellung und Nachbereitung

Ursache beheben, Zugriffe und Exporte überprüfen, erforderliche
Benachrichtigungen dokumentieren, Schutzmaßnahmen verbessern
und bei Bedarf die Dokumentation im `DSGVO/`-Ordner aktualisieren.

## Interne Vorfallakte (ausfüllen)

- Vorfall-ID / Datum und Uhrzeit: **[eintragen]**
- Meldeweg / meldende Person: **[eintragen]**
- Betroffene Systeme und Daten: **[eintragen]**
- Verantwortlicher / Auftragsverarbeiter: **[eintragen]**
- Erste Schutzmaßnahmen: **[eintragen]**
- Risikobewertung: **[eintragen]**
- Behörden- / Betroffeneninformation: **[eintragen]**
- Abschluss, Review und Freigabe: **[eintragen]**

Für Sicherheitslücken im **MForce-Quellcode** siehe
[SECURITY.md](../SECURITY.md). Datenschutzvorfälle einer
Nutzerorganisation müssen über deren eigene Meldewege laufen.
