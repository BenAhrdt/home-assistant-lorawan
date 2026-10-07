# Changelog

## 0.1.32 - 2026-10-07

- Änderungen an Downlink-Profilen und der Standardprofil-Startoption gelten für
  alle LNS-Integrationseinträge. Neue Einträge übernehmen diese Einstellungen.
- Hinweis zum Update: Bereits vorhandene Integrationseinträge werden durch das
  Update allein nicht synchronisiert. Erst beim nächsten Speichern einer Änderung
  im Downlink-Editor wird die dort angezeigte Konfiguration des ersten Eintrags
  auf alle vorhandenen Einträge übertragen.
- Beim Öffnen eines Geräts aus dem LoRaWAN-Dashboard bleibt der Rückweg zum
  Dashboard erhalten, auch bei Bedienung über die Tastatur.

## 0.1.31 - 2026-08-19

- Die Zuordnung für momentane Volumenwerte mit dem Feldnamen `Liter` verwendet
  jetzt die Home-Assistant-Geräteklasse `volume_storage`. Damit ist die
  Kombination mit der State-Class `measurement` gemäß der aktuellen
  Home-Assistant-Sensordokumentation gültig.

## 0.1.30 - 2026-08-19

- Windrichtung verwendet jetzt die neue Home-Assistant-State-Class
  `measurement_angle`. Dadurch werden Winkelstatistiken korrekt zirkulär
  berechnet und die Warnung zur ungültigen Kombination mit der Geräteklasse
  `wind_direction` behoben.

## 0.1.29 - 2026-08-06

- Geräte werden jetzt anhand der Kombination aus Config-Entry-ID und DevEUI
  registriert. Identische DevEUIs in mehreren TTN- oder ChirpStack-Einträgen
  bleiben dadurch getrennte Geräte mit ihren jeweils eigenen Entitäten.
- Bestehende, zuvor nur über die DevEUI zusammengeführte Geräte werden beim
  Start von den betroffenen Config-Einträgen gelöst und korrekt neu zugeordnet.
- Eintragsnamen werden beim Anlegen und Umbenennen ohne Beachtung von Groß- und
  Kleinschreibung auf Eindeutigkeit geprüft. Doppelte Namen werden mit einer
  verständlichen Fehlermeldung abgewiesen.

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
