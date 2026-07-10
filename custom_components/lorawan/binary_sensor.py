"""Binary sensor platform for LoRaWAN."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .assigner import assign_value
from .const import DOMAIN, SIGNAL_ADD_BINARY_SENSOR
from .entity import LoRaWANEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LoRaWAN binary sensors."""
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    @callback
    def add_entity(entity_key: str) -> None:
        if entity_key in added:
            return
        if runtime.get_value(entity_key) is None:
            return
        added.add(entity_key)
        async_add_entities([LoRaWANBinarySensor(runtime, entity_key)])

    for entity_key in runtime.entities_for_platform("binary_sensor"):
        add_entity(entity_key)

    entry.async_on_unload(
        add_runtime_listener(hass, SIGNAL_ADD_BINARY_SENSOR, entry.entry_id, add_entity)
    )


class LoRaWANBinarySensor(LoRaWANEntity, BinarySensorEntity):
    """A LoRaWAN binary sensor entity."""

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor value."""
        value = self.value
        if value is None:
            return None
        return _binary_state(value.value)

    @property
    def device_class(self) -> str | None:
        """Return the assigned binary sensor device class."""
        return assign_value("binary_sensor", self.device, self.value).device_class


def _binary_state(value) -> bool | None:
    """Return a Home Assistant binary state from common LoRaWAN payload values."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "on", "open", "opened", "geöffnet", "ein", "yes"}:
            return True
        if normalized in {"0", "false", "off", "closed", "geschlossen", "aus", "no"}:
            return False
    return None
