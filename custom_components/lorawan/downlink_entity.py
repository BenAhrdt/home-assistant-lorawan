"""Shared Home Assistant entities for configured LoRaWAN downlinks."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN
from .runtime import LoRaWANRuntime


class LoRaWANDownlinkEntity(Entity):
    """Base class for one device-specific downlink parameter."""

    _attr_has_entity_name = True

    def __init__(self, runtime: LoRaWANRuntime, entity_key: str) -> None:
        self.runtime = runtime
        self.entity_key = entity_key
        self._attr_unique_id = entity_key

    @property
    def control(self) -> dict[str, Any] | None:
        """Return the current control configuration."""
        return self.runtime.get_downlink_control(self.entity_key)

    @property
    def name(self) -> str | None:
        control = self.control
        return str(control["parameter"].get("name")) if control else None

    @property
    def device_info(self) -> DeviceInfo | None:
        control = self.control
        if control is None:
            return None
        device = control["device"]
        return {"identifiers": {(DOMAIN, device.dev_eui)}}

    @property
    def available(self) -> bool:
        return self.control is not None and self.runtime.connected

    def _send(self, value: Any) -> None:
        self.runtime.send_downlink_control(self.entity_key, value)
