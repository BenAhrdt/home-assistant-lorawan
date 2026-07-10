"""Base entity helpers for LoRaWAN."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_UPDATE_ENTITY
from .models import LoRaWANDevice, LoRaWANValue
from .runtime import LoRaWANRuntime

UnsubscribeCallback = Callable[[], None]


class LoRaWANEntity(Entity):
    """Base LoRaWAN entity."""

    _attr_has_entity_name = True

    def __init__(self, runtime: LoRaWANRuntime, entity_key: str) -> None:
        self.runtime = runtime
        self.entity_key = entity_key
        self._attr_unique_id = entity_key
        self._unsub_update: UnsubscribeCallback | None = None

    @property
    def value(self) -> LoRaWANValue | None:
        """Return the current LoRaWAN value."""
        return self.runtime.get_value(self.entity_key)

    @property
    def device(self) -> LoRaWANDevice | None:
        """Return the current LoRaWAN device."""
        return self.runtime.get_device(self.entity_key)

    @property
    def name(self) -> str | None:
        """Return the entity name."""
        value = self.value
        return value.name if value else None

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return Home Assistant device info."""
        device = self.device
        if device is None:
            return None
        info: DeviceInfo = {
            "identifiers": {(DOMAIN, device.dev_eui)},
            "name": device.device_name,
            "manufacturer": "LoRaWAN",
            "model": device.device_type or None,
            "sw_version": device.application_name,
        }
        return info

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        value = self.value
        device = self.device
        if value is None or device is None:
            return {}

        attributes: dict[str, Any] = {
            "application_id": device.application_id,
            "application_name": device.application_name,
            "dev_eui": device.dev_eui,
            "device_id": device.device_id,
            "raw_key": value.raw_key,
        }
        attributes.update(value.attributes)
        if isinstance(value.value, dict):
            attributes["raw_json"] = value.value
        return attributes

    async def async_added_to_hass(self) -> None:
        """Register update listener."""
        self._unsub_update = async_dispatcher_connect(
            self.hass,
            SIGNAL_UPDATE_ENTITY,
            self._handle_update_signal,
        )

    async def async_will_remove_from_hass(self) -> None:
        """Remove update listener."""
        if self._unsub_update is not None:
            self._unsub_update()
            self._unsub_update = None

    def _handle_update_signal(self, entity_key: str) -> None:
        if entity_key == self.entity_key:
            self.async_write_ha_state()


def state_value(value: Any) -> Any:
    """Return a Home Assistant state-safe value."""
    if isinstance(value, dict):
        return "received"
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return value
