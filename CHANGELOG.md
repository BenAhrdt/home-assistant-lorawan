# Changelog

## Unreleased

_(No unreleased changes.)_

## 0.1.50 - 2026-11-14

- Korrigiert die Migration bestehender `LastOpenDuration`-Entities für die
  tatsächliche normalisierte Entity-ID `lastopenduration`.

## 0.1.49 - 2026-11-14

- Bestehende `LastOpenDuration`-Entities migrieren einen automatisch
  gespeicherten Sekunden-Override auf die native Minuten-Einheit; explizite
  Nutzerüberschreibungen bleiben erhalten.

## 0.1.48 - 2026-11-14

- `LastOpenDuration` wird entsprechend dem Geräte-Decoder als Minutenwert mit
  der Einheit `min` statt als Sekundenwert dargestellt.

## 0.1.47 - 2026-11-14

- `LastWaterLeakDuration` wird als Minutenwert mit der Einheit `min` erkannt
  und ohne Nachkommastellen dargestellt.
- Dauerwerte mit der Einheit `s` werden ebenfalls ohne Nachkommastellen
  dargestellt.

## 0.1.46 - 2026-11-10

- AutoIntervall verwendet jetzt auch im Blueprint-Fallback und im Eingabefeld
  zuverlässig die Standardzeit 10:00:00 Uhr.

## 0.1.45 - 2026-11-10

- Monatswerte des AutoIntervall-Selectors als Zeichenketten serialisiert, damit
  der Blueprint-Import die Object-Selector-Optionen akzeptiert.

## 0.1.44 - 2026-11-10

- AutoIntervall-Zeitplanzeilen verwenden jetzt Monat und Tag ohne Jahresfeld.
  Die optionale Standardzeit ist 10:00:00 Uhr. Einzelne Zuweisungen ohne
  Bezeichnung verwenden bei genau einem Gerät dessen Gerätenamen als internen
  Fallback.

## 0.1.43 - 2026-11-10

- Fehlerkorrektur am verschachtelten AutoIntervall-Object-Selector: ungültige
  Feldoption entfernt, damit der Blueprint wieder importiert werden kann.

## 0.1.42 - 2026-11-10

- Der AutoIntervall-Blueprint verwendet wiederholbare Zeitplanzeilen mit
  wiederholbaren Geräte-/Intervall-Zuweisungen statt fester Zeitraum- und
  Zuweisungsfelder. Datumseinträge werden jährlich wiederholt; optionale
  Uhrzeiten werden minütlich ausgewertet.

## 0.1.41 - 2026-11-10

- Neuer zeitbasierter AutoIntervall-Blueprint mit bis zu fünf Jahreszeiträumen
  und jeweils fünf Geräte-/Intervall-Zuweisungen. Der Blueprint arbeitet ohne
  Uplink-Trigger, prüft den technischen `intervall`-Control und schreibt nur
  geänderte Werte.

## 0.1.40 - 2026-11-10

- Der Motorkalibrierungs-Blueprint zeigt keine veraltete Uplink-Zyklus-Auswahl
  mehr an. Die Standard-Uhrzeit ist 10:00 Uhr; Wochentag und Uhrzeit bleiben
  frei konfigurierbar.

## 0.1.39 - 2026-11-10

- Optionaler Blueprint für die wöchentliche Vicki-Motorkalibrierung mit
  Geräteauswahl, lokalem Wochentag und Uhrzeit. Der Blueprint arbeitet direkt
  mit dem stabilen `lorawan_control_key` der Downlink-Entitäten und benötigt
  keinen Uplink-Zeittrigger.

- Der `lorawan_uplink_schedule`-Trigger enthält zusätzlich einen versionierten
  Geräte- und Zeitplankontext sowie aktuelle Entity-Referenzen für Controls,
  Sensoren, Binary-Sensoren und Diagnose. Die bisherigen flachen Payload-Felder
  bleiben für bestehende Blueprints erhalten; Zustände werden nicht als veraltete
  Schnappschüsse mitgegeben.

- Der Raumtemperatur-Blueprint kann optional auf ausgewählte Vicki-Geräte
  begrenzt werden; die Geräteauswahl filtert die LoRaWAN-Integration auf das
  Modell `Vicki`. Eine leere Auswahl behält die Verarbeitung aller passenden
  Geräte bei. Ein neuer Blueprint wartet standardmäßig fünf Sekunden und drückt
  danach `Next Send Push` nur bei einem aktuell wartenden Downlink des
  auslösenden Geräts.

## 0.1.38 - 2026-11-06

- Optionaler Temperatur-Blueprint mit Label-Auswahl im Repository; Import-Link
  und ausführliche Wiki-Anleitung für Einrichtung, Diagnose und Updates.

- Drei Uplink-Diagnosezeitstempel standardmäßig deaktiviert; bestehende
  Aktivierungsentscheidungen bleiben erhalten. Trigger laufen unabhängig davon.

- Uplink-Zeittrigger enthält `controls`: stabile technische Schlüssel auf
  aktuelle Entity-IDs des auslösenden Geräts, etwa `external_temperature`.
- Auflösung bei Auslösung berücksichtigt Umbenennungen; deaktivierte, fremde
  oder mehrdeutige Controls werden nicht als Ziel angeboten.

## 0.1.37 - 2026-11-06

- Optionaler Uplink-Zeittrigger für alle Geräte: automatisch ermittelter
  Uplink-Abstand mit Vorlauf oder feste Zeit nach einem Uplink.
- Einstellbarer Mindestabstand filtert Folge-Uplinks, ohne den Zeitanker zu
  verschieben. Einmalige Timer werden bei neuen maßgeblichen Uplinks ersetzt.
- Gerätekonfiguration und Diagnosezeitpunkte auf der HA-Geräteseite;
  Gerätetrigger und Ereignis mit aktuellem Gerätenamen, Raum und Zeitdaten.

## 0.1.36 - 2026-11-02

- Applikationskreise durch dezente farbige Kreisflächen und klarere
  Zuordnungslinien sichtbar gemacht; LNS und Gateways stehen seitlich abseits.
- Funklinien im Ruhezustand zurückgenommen. Mouseover und Tastaturfokus auf
  eine Applikation zeigen auch die Funkwege aller zugehörigen Geräte.
- Neuer Layoutspeicher verwirft die bisherigen Positionen und den Viewport.

## 0.1.35 - 2026-11-02

- Geräte in vollständigen Kreisen um ihre jeweilige Applikation angeordnet;
  Gateways stehen separat oberhalb der Applikationsgruppen.
- Funklinien mit höherem Kontrast und größerer Strichstärke über den
  gestrichelten Zuordnungslinien dargestellt.
- Neuer Layoutspeicher übernimmt keine Positionen der bisherigen Anordnung.

## 0.1.34 - 2026-11-01

- Netzwerkansicht als räumliche Knotenkarte statt einer langen Spaltenansicht
  umgesetzt: LNS, Applikationen, Gateways und Geräte mit kompakten Symbolen.
- Alle Geräte sind im Standard sichtbar. Elliptische Applikationssektoren und
  Kollisionsabstände für Beschriftungen nutzen die verfügbare Breite und Höhe.
  LNS-Netzgruppen stehen auf breiten Bildschirmen nebeneinander.
- Funkempfang und logische Applikationszugehörigkeit erhalten verschiedene
  Linien; Legende und farbige LNS-Auswahl ergänzt. Klick auf LNS/Applikation
  fokussiert den entsprechenden Netzbereich.
- Alte Positionen und der stark verkleinerte Viewport der ersten Darstellung
  werden nicht in das neue Layout übernommen. Popup, Historie, Zoom, Drag-and-drop
  und Rücknavigation bleiben erhalten.

## 0.1.33 - 2026-11-01

- Neuer Netzwerk-Reiter mit LNS-Farben, Applikationsgruppen, Suche und LNS-Filter.
  Große Applikationen sind zunächst eingeklappt und lassen sich per Klick öffnen.
- Alle Gateway-Empfänge eines TTN-/ChirpStack-Uplinks werden berücksichtigt.
  Linien zeigen beobachtete Empfangswege und keine dauerhaften Funkverbindungen.
- Geräte-Popup mit letztem Uplink, Spreading Factor, Frequenz, Frame Counter,
  Port und RSSI/SNR je Gateway; bis zu 20 Uplinks je Gerät werden unabhängig
  von Rohdaten-Sensoren gespeichert und über Neustarts erhalten.
- Verschieben der Knoten und Ansicht, Mausrad-/Pinch-Zoom, Alles-einpassen und
  Layout-Reset. Layout und Filter werden je HA-Benutzer im jeweiligen Browser
  gespeichert. Die HA-Geräteseite erhält den Rückweg zur Netzwerkansicht.

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
