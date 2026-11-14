# LoRaWAN for Home Assistant

Home Assistant custom integration for receiving decoded LoRaWAN uplinks from MQTT.

This is the bridge-free Home Assistant port start for the LoRaWAN part of
`ioBroker.lorawan`. It listens to MQTT messages from The Things Stack / TTN or
ChirpStack, creates Home Assistant devices from incoming DevEUIs, and creates
entities from decoded payload values.

## Current Version

- Config flow in Home Assistant UI.
- Uses the existing Home Assistant MQTT integration.
- Supports decoded uplinks from:
  - The Things Stack / TTN
  - ChirpStack
- Creates Home Assistant devices automatically from incoming messages.
- Keeps devices with the same DevEUI separate for every configured TTN or
  ChirpStack connection by using the Home Assistant config entry together with
  the DevEUI as the device identifier.
- Requires a unique connection name when creating or renaming an integration
  entry. Name comparisons ignore surrounding whitespace and letter case.
- Creates sensor entities for numeric, text, and raw payload values. Numeric
  decoder values use two decimal places as their default display precision;
  percentage values are displayed without decimal places by default.
- Creates binary sensor entities for boolean decoded values.
- Supports downlinks, including optimistic switch controls that retain their
  displayed state across Home Assistant restarts.
- Supports user-composed Home Assistant entities that combine existing LoRaWAN
  uplink values with downlink controls:
  - Climate
  - Cover, including open/closed limit switches and optional travel-time based
    position estimation
  - Light
  - Humidifier and dehumidifier
  - Lock
  - Lawn mower
  - Vacuum
- Composite entities are configured per LoRaWAN device in the sidebar panel.
  Only assigned controls are exposed as supported features. Newly applied
  entities are available immediately for selection on the device card.
- The composite-entity editor supports German and English labels, collapsible
  entity-type sections, clearly selectable active signal levels, and matching
  icons on device cards.
- Dedicated MQTT broker credentials independent of Home Assistant's MQTT
  integration.
- Adds basic diagnostic attributes like DevEUI, application, topic, RSSI, SNR,
  spreading factor, frequency, frame port, and frame count when available.

<img width="1065" height="890" alt="image" src="https://github.com/user-attachments/assets/92530515-aca4-4701-9431-ecdff6a2a89b" />


## Blueprints

### Externe Raumtemperatur

Optionaler [Blueprint für externe Vicki-Raumtemperaturen](blueprints/automation/lorawan/room_external_temperature.yaml)
mit Label-Auswahl und optionaler Vicki-Geräteauswahl; eine Automation für alle
Räume. Eine leere Geräteauswahl lässt alle passenden Vicki-Geräte zu.
Voraussetzung: LoRaWAN ab 0.1.39.

[![Blueprint importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBenAhrdt%2Fhome-assistant-lorawan%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Florawan%2Froom_external_temperature.yaml)

Die ausführliche [Wiki-Anleitung](https://github.com/BenAhrdt/home-assistant-lorawan/wiki/07.01.-Blueprint-Room-temperature) beschreibt
Einrichtung, Prüfung und Updates. Bestehende manuelle Installationen können
erhalten bleiben.

### Verzögerter Next Send Push

Der [Blueprint für den verzögerten Next Send Push](blueprints/automation/lorawan/next_send_push.yaml)
wartet nach dem Uplink-Zeittrigger standardmäßig fünf Sekunden, damit andere
Blueprints ihre Downlinks sammeln können. Anschließend wird der aktuelle
`Next Send Hex`-Diagnosewert geprüft und der Push-Button des auslösenden Geräts
höchstens einmal betätigt. Eine leere Geräteauswahl gilt für alle LoRaWAN-Geräte;
die Auswahl kann den Push unabhängig von anderen triggerbasierten Blueprints auf
bestimmte Geräte begrenzen.

[![Blueprint importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBenAhrdt%2Fhome-assistant-lorawan%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Florawan%2Fnext_send_push.yaml)

### Automatische Intervallsteuerung

Der [zeitbasierte AutoIntervall-Blueprint](blueprints/automation/lorawan/automatic_interval.yaml)
arbeitet vollständig unabhängig vom Uplink-Trigger. Er bietet beliebig viele
wiederholbare Zeitplanzeilen; jede Zeile enthält Monat und Tag, optional eine
Uhrzeit (Standard 10:00:00) und beliebig viele wiederholbare
Geräte-/Intervall-Zuweisungen. So können unterschiedliche Geräte am selben
Zeitpunkt unterschiedliche Werte erhalten. Der Zeitpunkt wird jährlich
wiederholt. Bereits identische Werte werden nicht erneut geschrieben;
individuelle Gerätebereiche werden berücksichtigt.

[![Blueprint importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FBenAhrdt%2Fhome-assistant-lorawan%2Fmain%2Fblueprints%2Fautomation%2Florawan%2Fautomatic_interval.yaml%3Fversion%3D0.1.50)

Die ausführliche [Wiki-Anleitung](https://github.com/BenAhrdt/home-assistant-lorawan/wiki/07.04.-Blueprint-Automatic-interval)
beschreibt die Zeitraum- und Gerätezuweisungen.

### Wöchentliche Motorkalibrierung

Optionaler [Blueprint für die regelmäßige Vicki-Motorkalibrierung](blueprints/automation/lorawan/weekly_motor_calibration.yaml).
Wochentag, Uhrzeit und die Vicki-Geräte sind auswählbar. Die Kalibrierung wird
direkt zum lokalen Zeitpunkt ausgeführt und benötigt keinen Uplink-Zeittrigger.
Voraussetzung: LoRaWAN mit dem technischen `lorawan_control_key` an den
Downlink-Entitäten. Die Standard-Uhrzeit ist 10:00 Uhr; Wochentag und Uhrzeit
können beim Erstellen der Automation angepasst werden.

[![Blueprint importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FBenAhrdt%2Fhome-assistant-lorawan%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Florawan%2Fweekly_motor_calibration.yaml)

Die ausführliche [Wiki-Anleitung](https://github.com/BenAhrdt/home-assistant-lorawan/wiki/07.02.-Blueprint-Motor-calibration)
beschreibt Einrichtung, Diagnose und die zeitbasierte Ausführung.

## Wiki

[Link to HomeAssistant LoRaWAN Wiki](https://github.com/BenAhrdt/home-assistant-lorawan/wiki)

## Installation
(see Wiki for details)

Copy or install this repository as a HACS custom repository.

Manual test install:

```text
custom_components/lorawan
```

must exist inside your Home Assistant configuration directory. Restart Home
Assistant, then add **LoRaWAN** from **Settings -> Devices & services**.

Multiple TTN and ChirpStack entries can be configured at the same time. Each
entry must have a unique display name. A DevEUI occurring in more than one
entry is represented by a separate Home Assistant device for each entry.

## MQTT Topic Defaults

TTN:

```text
v3/+/devices/+/+
```

ChirpStack:

```text
application/+/device/+/event/+
```

The topic filters are fixed in code and selected from the configured network
server type.

## Notes

This integration expects the LoRaWAN network server to provide decoded payloads:

- TTN: `uplink_message.decoded_payload`
- ChirpStack: `object`

For both network servers, the normalizer detects the device type from the same
decoded-payload keys: `DeviceType`, `Device`, `Hardware_mode`, or `model_id`.
Key matching is case-insensitive. An existing device type learned from an
earlier uplink or entered manually is not overwritten by later uplinks.

Home Assistant entity metadata such as device class, state class, and unit is
assigned by field name only to decoded uplink values. Raw payload diagnostics,
remaining transport data, and downlink entities do not use these automatic
uplink assignments.

Raw payload diagnostic sensors can be enabled during setup.

## Composite Entities

Open a LoRaWAN device in the sidebar panel, select **Configure**, and then open
**Additional entities**. Add the required entity type and assign its uplink
state sources and optional downlink controls. Choose **Apply** to create or
update the Home Assistant entities without closing the editor. **Done** returns
to the device settings, where the new entity can be selected for display on the
device card.

For binary state sources, select whether `ON (true)` or `OFF (false)` represents
the active state. Cover entities can use either one or two limit switches, an
actual position source, or configured opening and closing times for an estimated
position. A real position source always takes precedence over estimation.

## DISCLAIMER
The rights of the trademarks and company names, remain with their owners and have no relation to this adapter. The fairuse policy must continue to be adhered to by the operator of the adapter. If this repository is forked, it must be cited as the source.

LoRa® is a registered trademark or service mark of Semtech Corporation or its affilantes.

LoRaWAN® is a licensed mark.

I have no affiliation with the mentioned brands or their subsidiaries, logos, or trademarks, nor am I endorsed by them.

## License
MIT License

Copyright (c) 2025-2026 BenAhrdt <bsahrdt@gmail.com>  
Copyright (c) 2025-2026 Joerg Froehner <LoraWan@hafenmeister.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Network view

The **Network** tab shows a spatial node map of LNS connections, applications,
gateways and devices, using the configured connection colors. Gateways are shared between applications within
one LNS; identical gateway/application/device IDs on different LNS connections
remain separate. All devices are visible by default. Application sectors spread around their
LNS; label-aware collision separation keeps the layout compact and deterministic.
LNS islands sit beside each other on wide screens and stack on narrow screens.
Click an application or LNS node to focus that part of the map.

Lines represent gateway receptions reported in each device's **latest uplink**,
not permanent connections or guaranteed downlink routes. All entries from TTN
`rx_metadata` and ChirpStack `rxInfo` are retained. Missing metadata keeps the
device visible without an invented gateway. Gateway details show when it was
last observed, rather than assuming a gateway online/offline state.

Click a device for radio diagnostics, selected device-tile values, and the last
20 uplinks with decoded values and per-gateway RSSI/SNR. This history starts
collecting after the update, survives HA restarts, and does not depend on raw or
remaining sensor settings. Join/status/downlink events do not replace it.
Device availability continues to use the integration's existing activity timeout.

Drag nodes to arrange them, drag the canvas to pan, and use the mouse wheel or
two-finger pinch to zoom. **Fit all** adjusts the viewport; **Reset layout** also
restores automatic positions. Positions, filters and viewport are stored per HA user in the current
browser, not synchronized between browsers. Search matches device names,
DevEUIs, applications and gateways. The device-page button preserves the return
path to `/lorawan?view=network` and the saved view.

Network regression checks: `python3 -m unittest discover -s tests -v` and
`node tests/network.test.cjs` (the latter requires Node.js).

Version 0.1.34 replaces the initial column layout with a spatial map and uses a
new layout-storage key, so the previous tiny viewport is not restored. Solid
lines indicate radio reception; faint dashed lines indicate logical membership.

## Integration-calculated uplink triggers

Every device has optional **LoRaWAN uplink** configuration entities on its Home
Assistant device page. This is a calculation performed by the integration, not
an event reported by the physical device. It does not send downlinks.

- **Trigger mode** defaults to disabled. Choose **Automatic** to estimate the
  next uplink from the last two accepted uplinks and trigger before it, or
  **Time after uplink** to trigger a fixed number of seconds after an accepted
  uplink.
- **Lead time** defaults to 20 seconds; **time after uplink** to 580 seconds.
- **Minimum uplink spacing** defaults to 30 seconds. Uplinks arriving sooner
  than this after the accepted anchor are ignored for scheduling only. They
  neither change the interval nor move or duplicate the pending trigger.
- The automatic interval is measured between accepted uplinks, not averaged.
  Choose a minimum spacing appropriate to the device's normal reporting cycle.
  Predictions are useful for periodic devices; irregular uplinks remain uncertain.
- Diagnostic timestamp entities are disabled by default and can be enabled
  individually on the device page without affecting trigger execution. Existing
  registry choices are preserved. They show the next calculated trigger, next expected
  uplink (automatic mode), and last trigger. Names carry the LoRaWAN prefix and
  attributes identify the integration as the source.

In an automation, choose the device and **LoRaWAN: calculated uplink time
reached**. Alternatively, listen for the `lorawan_uplink_schedule` event.
Both expose the payload through `trigger.event.data`:

```yaml
triggers:
  - trigger: event
    event_type: lorawan_uplink_schedule
    event_data:
      device_id: YOUR_HOME_ASSISTANT_DEVICE_ID
actions:
  - action: persistent_notification.create
    data:
      message: >-
        {{ trigger.event.data.device_name }}:
        {{ trigger.event.data.area_name or 'No area' }}
```

Payload fields:

| Field | Meaning |
| --- | --- |
| `source` | `lorawan` |
| `mode` | `automatic` or `after_uplink` |
| `device_id`, `dev_eui`, `config_entry_id` | HA device, radio identity, and LNS entry |
| `device_name` | Current HA user-defined name, falling back to the device name |
| `area_id`, `area_name` | Current device area, or `null` if unassigned |
| `interval_seconds` | Last accepted uplink interval; `null` for the first anchor |
| `offset_seconds` | Negative lead in automatic mode; positive delay otherwise |
| `last_uplink` | Accepted anchor's local reception time, in UTC ISO format |
| `expected_next_uplink` | Predicted UTC ISO timestamp, or `null` in fixed-delay mode |
| `scheduled_for` | Scheduled UTC ISO trigger timestamp |

Names and area assignments are resolved at trigger time. Settings survive reloads
and restarts; anchors and pending timers deliberately do not. Changing any setting
cancels the pending timer and starts learning again with fresh uplinks. Automatic
mode needs two accepted uplinks; fixed-delay mode needs one. Each plan fires at
most once and never repeats without a new accepted uplink. If the automatic lead
is greater than or equal to the observed interval, no trigger is scheduled for
that cycle. Only actual `up`/`uplink` messages participate, not join, acknowledgement,
or downlink messages. Predictions do not guarantee a radio receive window.

### Control references in the trigger payload

`trigger.event.data.controls` maps stable technical keys to the current entity
IDs of writable LoRaWAN entities belonging to the triggering device and LNS.
For example (actual entity IDs depend on your installation):

```yaml
controls:
  external_temperature: number.vicki_externaltemperature
  target_temperature: number.vicki_targettemperature
  mode2: switch.vicki_mode2
```

A Vicki automation can therefore address the target without an entity selector:

```yaml
action: number.set_value
target:
  entity_id: "{{ trigger.event.data.controls.external_temperature }}"
data:
  value: "{{ room_temperature }}"
```

This action fragment assumes the automation has already resolved and validated
`room_temperature`, and checked that `external_temperature` exists in `controls`.
An external automation or blueprint can use the trigger's `area_id` and a label
such as `primaryRoomTemperature` on the preferred sensor entity. Sensor selection
and label assignment are not performed by the integration.

### Structured device context

The event also carries a versioned context for blueprints that need more than a
single control:

```yaml
schema_version: 1
trigger_id: "entry:DEV_EUI:2026-11-06T12:00:00+00:00"
triggered_at: "2026-11-06T12:00:00+00:00"
device:
  ha_device_id: "..."
  lorawan_device_id: "..."
  dev_eui: "..."
  name: "Vicki living room"
  network_name: "Vicki-01"
  device_type: "Vicki"
  area_id: "..."
  area_name: "Living room"
  config_entry_id: "..."
  network: "ttn"
  application_id: "..."
  application_name: "..."
schedule:
  mode: automatic
  interval_seconds: 600
  offset_seconds: -20
  last_uplink: "..."
  expected_next_uplink: "..."
  scheduled_for: "..."
entities:
  controls:
    external_temperature: number.vicki_external_temperature
    next_send_push: button.vicki_next_send_push
  sensors:
    room_temperature: sensor.room_temperature
  binary_sensors:
    online: binary_sensor.vicki_online
  diagnostics:
    next_send_hex: sensor.vicki_next_send_hex
    last_send_hex: sensor.vicki_last_send_hex
```

The existing top-level fields and `controls` mapping remain for compatibility.
The structured mappings contain only active, current registry entities for the
triggering device and LNS entry. Technical keys are derived from integration
keys and stable unique IDs, not friendly names. Disabled, stale, foreign and
ambiguous entities are omitted. The event carries entity references rather than
state snapshots; a blueprint should read the referenced state when it acts,
which is important after a delay such as a deferred `Next Send Push`.

Each active LoRaWAN downlink control also exposes its normalized technical key
as the `lorawan_control_key` entity attribute. A time-based blueprint can use
`device_entities(device_id)` and this attribute to find a specific control such
as `motor_calibration` without relying on a user-editable entity ID or a prior
uplink event.

Downlink keys come from technical profile parameter names, normalized to snake
case (`ExternalTemperature` → `external_temperature`, `Mode2` → `mode2`), or an
explicit `automation_key` in the parameter definition. HA friendly-name and
entity-ID changes do not change these keys. Changing the technical profile name
changes its key unless an explicit key is provided. Other writable entities,
including composed entities and configuration controls, use their stable unique-ID
suffix with the entity domain as prefix (for example `climate_<definition-id>`).

Entity IDs are resolved from the registry when the event fires. Disabled entities,
read-only sensors, stale downlink entries and entities from other devices or LNS
entries are excluded. Ambiguous keys are omitted rather than choosing a target
arbitrarily. An empty device mapping is emitted as `controls: {}`. Availability
and sensor validity should still be checked by the consuming automation.
