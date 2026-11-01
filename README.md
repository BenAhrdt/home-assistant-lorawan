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
