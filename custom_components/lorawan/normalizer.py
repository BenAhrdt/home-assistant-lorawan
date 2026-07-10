"""Normalize TTN and ChirpStack MQTT payloads."""

from __future__ import annotations

import base64
import copy
from collections.abc import Iterable
from typing import Any

from .models import LoRaWANDevice, LoRaWANMessage, LoRaWANValue


def normalize_message(topic: str, payload: dict[str, Any]) -> LoRaWANMessage | None:
    """Normalize one MQTT message from a supported LoRaWAN network server."""
    if topic.startswith("v3/") or "end_device_ids" in payload:
        return _normalize_ttn(topic, payload)
    if topic.startswith("application/") or "deviceInfo" in payload:
        return _normalize_chirpstack(topic, payload)
    return None


def _normalize_ttn(topic: str, payload: dict[str, Any]) -> LoRaWANMessage | None:
    message_type = topic.rsplit("/", 1)[-1]
    ids = payload.get("end_device_ids") or {}
    uplink = payload.get("uplink_message") or {}
    decoded_payload = uplink.get("decoded_payload") or {}

    dev_eui = _clean_id(ids.get("dev_eui") or ids.get("device_id"))
    if not dev_eui:
        return None

    application = ids.get("application_ids") or {}
    device = LoRaWANDevice(
        application_id=str(application.get("application_id") or "unknown"),
        application_name=str(application.get("application_id") or "unknown"),
        dev_eui=dev_eui,
        device_id=str(ids.get("device_id") or dev_eui),
        device_name=str(ids.get("device_id") or dev_eui),
        device_type=_first_string(decoded_payload, ("devicetype", "device", "Device", "model_id")),
    )

    attributes = {
        "network": "ttn",
        "received_at": payload.get("received_at") or uplink.get("received_at"),
        "f_port": uplink.get("f_port"),
        "f_cnt": uplink.get("f_cnt"),
        "topic": topic,
    }
    attributes.update(_ttn_radio_attributes(uplink))

    return LoRaWANMessage(
        topic=topic,
        message_type=message_type,
        device=device,
        decoded=_flatten_values(decoded_payload),
        raw=_raw_values(
            payload=uplink.get("frm_payload"),
            raw_json=payload,
        ),
        remaining=_remaining_values(
            raw_json=_without_paths(
                payload,
                (
                    ("uplink_message", "decoded_payload"),
                    ("uplink_message", "frm_payload"),
                ),
            )
        ),
        attributes=_compact(attributes),
    )


def _normalize_chirpstack(topic: str, payload: dict[str, Any]) -> LoRaWANMessage | None:
    message_type = topic.rsplit("/", 1)[-1]
    info = payload.get("deviceInfo") or {}
    decoded_payload = payload.get("object") or {}

    dev_eui = _clean_id(info.get("devEui") or _topic_part(topic, "device"))
    if not dev_eui:
        return None

    device = LoRaWANDevice(
        application_id=str(info.get("applicationId") or _topic_part(topic, "application") or "unknown"),
        application_name=str(info.get("applicationName") or "unknown"),
        dev_eui=dev_eui,
        device_id=str(info.get("deviceName") or dev_eui),
        device_name=str(info.get("deviceName") or dev_eui),
        device_type=str(info.get("deviceProfileName") or "") or _first_string(
            decoded_payload,
            ("devicetype", "Device", "Hardware_mode", "model_id"),
        ),
    )

    attributes = {
        "network": "chirpstack",
        "received_at": payload.get("time"),
        "f_port": payload.get("fPort"),
        "f_cnt": payload.get("fCnt"),
        "topic": topic,
    }
    attributes.update(_chirpstack_radio_attributes(payload))

    return LoRaWANMessage(
        topic=topic,
        message_type=message_type,
        device=device,
        decoded=_flatten_values(decoded_payload),
        raw=_raw_values(
            payload=payload.get("data"),
            raw_json=payload,
        ),
        remaining=_remaining_values(
            raw_json=_without_paths(
                payload,
                (
                    ("object",),
                    ("data",),
                ),
            )
        ),
        attributes=_compact(attributes),
    )


def _flatten_values(data: dict[str, Any], prefix: str = "") -> list[LoRaWANValue]:
    values: list[LoRaWANValue] = []
    for key, value in data.items():
        raw_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            values.extend(_flatten_values(value, raw_key))
            continue
        if isinstance(value, list):
            for index, item in enumerate(value):
                item_key = f"{raw_key}.{index}"
                if isinstance(item, dict):
                    values.extend(_flatten_values(item, item_key))
                else:
                    values.append(
                        LoRaWANValue(
                            key=_slugify(item_key),
                            raw_key=item_key,
                            name=_friendly_name(item_key),
                            value=item,
                        )
                    )
            continue
        values.append(
            LoRaWANValue(
                key=_slugify(raw_key),
                raw_key=raw_key,
                name=_friendly_name(raw_key),
                value=value,
            )
        )
    return values


def _raw_values(payload: str | None, raw_json: dict[str, Any]) -> list[LoRaWANValue]:
    values = [
        LoRaWANValue(
            key="raw_json",
            raw_key="raw.json",
            name="Raw JSON",
            value=raw_json,
        )
    ]
    if payload:
        values.extend(
            [
                LoRaWANValue("raw_base64", "Raw Base64", payload, "raw.base64"),
                LoRaWANValue("raw_hex", "Raw Hex", _base64_to_hex(payload), "raw.hex"),
                LoRaWANValue("raw_string", "Raw String", _base64_to_string(payload), "raw.string"),
            ]
        )
    return values


def _remaining_values(raw_json: dict[str, Any]) -> list[LoRaWANValue]:
    values = [
        LoRaWANValue(
            key="remaining_json",
            raw_key="remaining.json",
            name="Remaining JSON",
            value=raw_json,
        )
    ]
    values.extend(_flatten_values(raw_json, "remaining"))
    return values


def _without_paths(
    data: dict[str, Any],
    paths: Iterable[tuple[str, ...]],
) -> dict[str, Any]:
    result = copy.deepcopy(data)
    for path in paths:
        current = result
        for key in path[:-1]:
            next_value = current.get(key)
            if not isinstance(next_value, dict):
                current = {}
                break
            current = next_value
        if current:
            current.pop(path[-1], None)
    return result


def _ttn_radio_attributes(uplink: dict[str, Any]) -> dict[str, Any]:
    metadata = (uplink.get("rx_metadata") or [{}])[0] or {}
    settings = uplink.get("settings") or {}
    lora = ((settings.get("data_rate") or {}).get("lora") or {})
    return {
        "gateway_id": ((metadata.get("gateway_ids") or {}).get("gateway_id")),
        "rssi": metadata.get("rssi") or metadata.get("channel_rssi"),
        "snr": metadata.get("snr"),
        "frequency": settings.get("frequency"),
        "spreading_factor": lora.get("spreading_factor"),
    }


def _chirpstack_radio_attributes(payload: dict[str, Any]) -> dict[str, Any]:
    rx_info = (payload.get("rxInfo") or [{}])[0] or {}
    lora = (((payload.get("txInfo") or {}).get("modulation") or {}).get("lora") or {})
    return {
        "gateway_id": rx_info.get("gatewayId"),
        "rssi": rx_info.get("rssi"),
        "snr": rx_info.get("snr"),
        "frequency": (payload.get("txInfo") or {}).get("frequency"),
        "spreading_factor": lora.get("spreadingFactor"),
    }


def _topic_part(topic: str, marker: str) -> str | None:
    parts = topic.split("/")
    try:
        return parts[parts.index(marker) + 1]
    except (ValueError, IndexError):
        return None


def _first_string(data: dict[str, Any], keys: Iterable[str]) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _base64_to_hex(value: str) -> str:
    try:
        return base64.b64decode(value).hex().upper()
    except Exception:
        return ""


def _base64_to_string(value: str) -> str:
    try:
        return base64.b64decode(value).decode(errors="replace")
    except Exception:
        return ""


def _compact(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None and value != ""}


def _clean_id(value: Any) -> str:
    return _slugify(str(value or "")).upper()


def _friendly_name(value: str) -> str:
    return value.replace("_", " ").replace(".", " ").title()


def _slugify(value: str) -> str:
    result = []
    for char in value:
        if char.isalnum():
            result.append(char.lower())
        else:
            result.append("_")
    slug = "".join(result).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug
