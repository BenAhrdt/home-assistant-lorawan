"""Downlink profile handling and ioBroker-compatible payload serialization."""

from __future__ import annotations

import base64
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


DEFAULT_PARAMETER = {
    "port": 1,
    "priority": "NORMAL",
    "confirmed": False,
    "type": "number",
    "front": "",
    "end": "",
    "lengthInByte": 1,
    "on": "",
    "off": "",
    "onClick": "",
    "multiplyfaktor": 1,
    "decimalPlaces": 0,
    "swap": False,
    "limitMin": False,
    "limitMinValue": 0,
    "limitMax": False,
    "limitMaxValue": 0,
    "unit": "",
    "crc": "noCrc",
    "withStates": False,
    "statesValue": "",
}

# The profile format intentionally matches the ioBroker adapter JSON files. More
# profiles can be added in the Downlinks tab without a code change.
FALLBACK_PROFILES: list[dict[str, Any]] = [
    {
        "deviceType": "Dragino",
        "sendWithUplink": "disabled",
        "port": 2,
        "priority": "NORMAL",
        "confirmed": False,
        "downlinkParameter": [
            {
                "name": "Intervall",
                "port": 1,
                "type": "number",
                "front": "01",
                "lengthInByte": 3,
                "multiplyfaktor": 60,
                "unit": "min",
                "limitMin": True,
                "limitMinValue": 0,
                "limitMax": True,
                "limitMaxValue": 1440,
            },
            {"name": "Reboot", "port": 1, "type": "button", "onClick": "04FF"},
        ],
    },
    {
        "deviceType": "Vicki",
        "sendWithUplink": "enabled & collect",
        "port": 1,
        "priority": "NORMAL",
        "confirmed": False,
        "downlinkParameter": [
            {
                "name": "Intervall",
                "type": "number",
                "front": "02",
                "end": "12",
                "lengthInByte": 1,
                "multiplyfaktor": 1,
                "unit": "Minuten",
                "limitMin": True,
                "limitMinValue": 5,
                "limitMax": True,
                "limitMaxValue": 360,
            },
            {
                "name": "TargetTemperature",
                "type": "number",
                "front": "51",
                "lengthInByte": 2,
                "multiplyfaktor": 10,
                "decimalPlaces": 1,
                "unit": "°C",
                "limitMin": True,
                "limitMinValue": 6,
                "limitMax": True,
                "limitMaxValue": 30,
            },
            {"name": "GetInfos", "type": "button", "onClick": "041215184634363D"},
            {"name": "MotorCalibration", "type": "button", "onClick": "03"},
            {
                "name": "ChildLock",
                "type": "boolean",
                "on": "070114",
                "off": "070014",
            },
            {
                "name": "OpenWindowDetection",
                "type": "boolean",
                "on": "4501060F46",
                "off": "4500060F46",
            },
        ],
    },
]


def _builtin_profiles() -> list[dict[str, Any]]:
    """Load the complete ioBroker device-profile collection bundled with HA."""
    profiles = []
    for path in sorted((Path(__file__).parent / "profiles").glob("*.json")):
        try:
            profiles.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return profiles or FALLBACK_PROFILES


BUILTIN_PROFILES = _builtin_profiles()

INTERNAL_BASE_PROFILE: dict[str, Any] = {
    "deviceType": "internalBaseDevice",
    "sendWithUplink": "disabled",
    "downlinkParameter": [
        {"name": "push", "type": "json", "networks": ["ttn", "chirpstack"]},
        {"name": "replace", "type": "json", "networks": ["ttn"]},
        {
            "name": "CustomSend",
            "type": "string",
            "networks": ["ttn", "chirpstack"],
        },
    ],
}


def merged_profiles(configured: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Merge user profiles over built-ins by device type, honoring tombstones."""
    profiles = {
        INTERNAL_BASE_PROFILE["deviceType"]: deepcopy(INTERNAL_BASE_PROFILE),
        **{profile["deviceType"]: deepcopy(profile) for profile in BUILTIN_PROFILES},
    }
    for profile in configured or []:
        if profile.get("deviceType"):
            device_type = str(profile["deviceType"])
            if profile.get("_deleted"):
                profiles.pop(device_type, None)
            else:
                profiles[device_type] = deepcopy(profile)
    return list(profiles.values())


def profile_for_device(profiles: list[dict[str, Any]], device_type: str | None) -> dict[str, Any] | None:
    """Return the longest profile prefix matching a device type.

    This mirrors the ioBroker adapter: for example, ``Dragino XY`` matches
    ``Dragino`` and a longer, more specific profile wins over a shorter one.
    """
    wanted = str(device_type or "").casefold()
    matches = [
        profile
        for profile in profiles
        if profile.get("deviceType") != INTERNAL_BASE_PROFILE["deviceType"]
        and wanted.startswith(str(profile.get("deviceType", "")).casefold())
        and profile.get("deviceType")
    ]
    if matches:
        return max(matches, key=lambda profile: len(str(profile["deviceType"])))
    return next(
        (
            profile
            for profile in profiles
            if profile.get("deviceType") == INTERNAL_BASE_PROFILE["deviceType"]
        ),
        None,
    )


def parameter_payload(parameter: dict[str, Any], value: Any) -> str:
    """Serialize a command value into the ioBroker profile's uppercase hex payload."""
    data = {**DEFAULT_PARAMETER, **parameter}
    kind = data["type"]
    if kind == "button":
        payload = str(data["onClick"])
    elif kind == "boolean":
        payload = str(data["on"] if bool(value) else data["off"])
    elif kind == "number":
        numeric = float(value)
        decimal_places = max(0, int(data.get("decimalPlaces", 0)))
        if abs(numeric - round(numeric, decimal_places)) > 1e-9:
            raise ValueError(
                f"Wert darf höchstens {decimal_places} Dezimalstellen haben"
            )
        if data["limitMin"] and numeric < float(data["limitMinValue"]):
            raise ValueError("Wert liegt unter dem konfigurierten Minimum")
        if data["limitMax"] and numeric > float(data["limitMaxValue"]):
            raise ValueError("Wert liegt über dem konfigurierten Maximum")
        scaled = round(numeric * float(data["multiplyfaktor"]))
        length = int(data["lengthInByte"])
        minimum, maximum = -(1 << (length * 8 - 1)), (1 << (length * 8)) - 1
        if not minimum <= scaled <= maximum:
            raise ValueError("Wert passt nicht in die konfigurierte Byte-Länge")
        payload = (scaled & maximum).to_bytes(length, "big").hex()
        if data["swap"]:
            payload = bytes.fromhex(payload)[::-1].hex()
        payload = f"{data['front']}{payload}{data['end']}"
    elif kind == "ascii":
        raw = str(value).encode("ascii")
        payload = raw[: int(data["lengthInByte"])].rjust(int(data["lengthInByte"]), b"\0").hex()
        payload = f"{data['front']}{payload}{data['end']}"
    elif kind == "string":
        payload = f"{data['front']}{value}{data['end']}"
    else:
        raise ValueError(f"Nicht unterstützter Downlink-Typ: {kind}")
    _validate_hex(payload)
    return _with_crc(payload, str(data["crc"]))


def state_options(parameter: dict[str, Any]) -> dict[str, str]:
    """Return raw values mapped to human-readable HA select options."""
    if not parameter.get("withStates"):
        return {}
    raw_states = parameter.get("statesValue") or {}
    if isinstance(raw_states, str):
        try:
            raw_states = json.loads(raw_states)
        except json.JSONDecodeError:
            return {}
    if not isinstance(raw_states, dict):
        return {}
    return {
        str(raw_value): f"{label} ({raw_value})"
        for raw_value, label in raw_states.items()
        if str(label).strip()
    }


def _with_crc(payload: str, crc: str) -> str:
    """Append the ioBroker-compatible CRC variant to a hexadecimal payload."""
    if crc == "noCrc":
        return payload.upper()
    raw = bytes.fromhex(payload)
    if crc == "CRC-8":
        checksum = _crc8(raw)
        return f"{payload}{checksum:02X}".upper()
    if crc in {"KERMIT", "KERMIT.LittleEndian"}:
        checksum = _crc16_kermit(raw)
        encoded = checksum.to_bytes(2, "big")
        if crc.endswith(".LittleEndian"):
            encoded = encoded[::-1]
        return f"{payload}{encoded.hex()}".upper()
    raise ValueError(f"Nicht unterstützte CRC-Variante: {crc}")


def _crc8(data: bytes) -> int:
    """Return the CRC-8 checksum (poly 0x07) used by easy-crc's CRC-8 mode."""
    checksum = 0
    for byte in data:
        checksum ^= byte
        for _ in range(8):
            checksum = ((checksum << 1) ^ 0x07) & 0xFF if checksum & 0x80 else (checksum << 1) & 0xFF
    return checksum


def _crc16_kermit(data: bytes) -> int:
    """Return the reflected CRC-16/KERMIT checksum."""
    checksum = 0
    for byte in data:
        checksum ^= byte
        for _ in range(8):
            checksum = (checksum >> 1) ^ 0x8408 if checksum & 1 else checksum >> 1
    return checksum & 0xFFFF


def downlink_message(network: str, device: Any, profile: dict[str, Any], payload_hex: str) -> tuple[str, dict[str, Any]]:
    """Return the MQTT topic and network-server payload for one downlink."""
    payload = base64.b64encode(bytes.fromhex(payload_hex)).decode()
    port = int(profile.get("port", 1))
    confirmed = bool(profile.get("confirmed", False))
    priority = str(profile.get("priority", "NORMAL"))
    if network == "ttn":
        application, _, tenant = device.application_name.partition("@")
        app = application or device.application_id
        topic = f"v3/{app}{'@' + tenant if tenant else ''}/devices/{device.device_id}/down/push"
        return topic, {"downlinks": [{"f_port": port, "frm_payload": payload, "priority": priority, "confirmed": confirmed}]}
    if network == "chirpstack":
        topic = f"application/{device.application_id}/device/{device.dev_eui}/command/down"
        return topic, {"devEui": device.dev_eui, "confirmed": confirmed, "fPort": port, "data": payload}
    raise ValueError("Unbekannter LoRaWAN-Netzwerkserver")


def _validate_hex(value: str) -> None:
    if len(value) % 2 or any(char not in "0123456789abcdefABCDEF" for char in value):
        raise ValueError("Downlink-Payload muss eine gültige gerade Hex-Zeichenfolge sein")
