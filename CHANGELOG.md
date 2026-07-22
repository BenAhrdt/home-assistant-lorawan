# Changelog

## 0.1.28 - 2026-07-22

- Zusammengesetzte Cover-, Light-, Humidifier-, Lock-, Mähroboter- und
  Vacuum-Entitäten ergänzt.
- Cover unterstützen optionale Endschalter für geöffnete und geschlossene
  Endlagen, echte Positionswerte sowie eine laufzeitbasierte Positionsschätzung.
- Unterstützte Funktionen werden automatisch aus den zugewiesenen Downlinks
  abgeleitet.
- Editor für zusätzliche Entitäten übersichtlicher strukturiert und alle
  Entitätstypen auf- und zuklappbar gemacht.
- Aktiven Binärzustand eindeutig als `EIN (true)` oder `AUS (false)` auswählbar
  gemacht.
- Deutsche und englische Beschriftungen, lokalisierte Geräteklassen und
  Standardnamen ergänzt.
- Neue Entitäten stehen nach **Übernehmen** ohne erneutes Öffnen direkt für die
  Gerätekachel zur Verfügung.
- Klicks auf die vollständige graue Entitätszeile öffnen die Entität; nur Klicks
  außerhalb der Zeile öffnen das Gerät.
- Passende Gerätekachel-Icons für alle zusammengesetzten Entitätstypen ergänzt.

## 0.1.27 - 2026-07-21

- LT22222-Downlink-Profil aktualisiert und Parameter verständlicher benannt.
- LT22222-Befehle für Arbeitsmodus und Triggermodus ergänzt.

## 0.1.26 - 2026-07-21

- Downlink-Profile einzeln oder gesammelt als ioBroker-kompatible JSON-Dateien exportieren.
- Einzelne, mehrere oder gesammelt exportierte Profile importieren.
- Optional vorhandene Profile beim Import überschreiben und die Auswahl im Browser speichern.
- Mitgelieferte Standardprofile gezielt auswählen, importieren oder auf ihren Standard zurücksetzen.
- Eigene und mitgelieferte Profile löschen.
- Optional fehlende und neu hinzugekommene Standardprofile beim Home-Assistant-Start laden.
- Importfortschritt anzeigen und geöffnete Profile nach dem Import unmittelbar aktualisieren.
