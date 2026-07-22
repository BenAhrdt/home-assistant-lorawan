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

## Not Yet Included

- Automated tests against a Home Assistant test harness.

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
