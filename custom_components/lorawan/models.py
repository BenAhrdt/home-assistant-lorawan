"""Shared models for LoRaWAN runtime data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LoRaWANDevice:
    """A LoRaWAN device seen on MQTT."""

    application_id: str
    application_name: str
    dev_eui: str
    device_id: str
    device_name: str
    device_type: str | None = None


@dataclass(slots=True)
class LoRaWANValue:
    """One flattened LoRaWAN value."""

    key: str
    name: str
    value: Any
    raw_key: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LoRaWANMessage:
    """A normalized LoRaWAN MQTT message."""

    topic: str
    message_type: str
    device: LoRaWANDevice
    decoded: list[LoRaWANValue]
    raw: list[LoRaWANValue]
    remaining: list[LoRaWANValue]
    attributes: dict[str, Any] = field(default_factory=dict)
