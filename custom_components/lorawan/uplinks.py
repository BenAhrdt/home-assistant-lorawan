"""Bounded, sensor-independent uplink history for the network view."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .models import LoRaWANMessage

UPLINK_HISTORY_LIMIT = 20


def remember_uplink(
    history: dict[str, list[dict[str, Any]]],
    message: LoRaWANMessage,
    observed_at: str,
) -> None:
    """Keep actual uplinks only; protocol events must not replace radio links."""
    if message.message_type.casefold() not in {"up", "uplink"}:
        return
    attributes = message.attributes
    record = {
        "observed_at": observed_at,
        "received_at": attributes.get("received_at") or observed_at,
        "f_cnt": attributes.get("f_cnt"),
        "f_port": attributes.get("f_port"),
        "frequency": attributes.get("frequency"),
        "spreading_factor": attributes.get("spreading_factor"),
        "gateways": deepcopy(attributes.get("gateways") or []),
        "decoded": {value.raw_key: deepcopy(value.value) for value in message.decoded},
    }
    records = history.setdefault(message.device.dev_eui, [])
    records.insert(0, record)
    del records[UPLINK_HISTORY_LIMIT:]
