# LoRaWAN for Home Assistant

Home Assistant custom integration for receiving decoded LoRaWAN uplinks from MQTT.

This is the bridge-free Home Assistant port start for the LoRaWAN part of
`ioBroker.lorawan`. It listens to MQTT messages from The Things Stack / TTN or
ChirpStack, creates Home Assistant devices from incoming DevEUIs, and creates
entities from decoded payload values.

## Current MVP

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
- Dedicated MQTT broker credentials independent of Home Assistant's MQTT
  integration.
- Adds basic diagnostic attributes like DevEUI, application, topic, RSSI, SNR,
  spreading factor, frequency, frame port, and frame count when available.

<img width="1065" height="890" alt="image" src="https://github.com/user-attachments/assets/92530515-aca4-4701-9431-ecdff6a2a89b" />

## Not Yet Included

- Automated tests against a Home Assistant test harness.

## Installation

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
