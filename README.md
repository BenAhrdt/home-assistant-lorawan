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
- Creates sensor entities for numeric, text, and raw payload values.
- Creates binary sensor entities for boolean decoded values.
- Adds basic diagnostic attributes like DevEUI, application, topic, RSSI, SNR,
  spreading factor, frequency, frame port, and frame count when available.

## Not Yet Included

- Downlinks.
- Device profile UI.
- Import of ioBroker downlink profiles.
- Dedicated MQTT broker credentials independent of Home Assistant's MQTT
  integration.
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

Raw payload diagnostic sensors can be enabled during setup.
