"""Sensor platform for LoRaWAN."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .assigner import assign_value
from .const import DOMAIN, SIGNAL_ADD_SENSOR
from .entity import LoRaWANEntity, state_value
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LoRaWAN sensors."""
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    @callback
    def add_entity(entity_key: str) -> None:
        if entity_key in added:
            return
        if runtime.get_value(entity_key) is None:
            return
        added.add(entity_key)
        async_add_entities([LoRaWANSensor(runtime, entity_key)])

    for entity_key in runtime.entities_for_platform("sensor"):
        add_entity(entity_key)

    entry.async_on_unload(
        add_runtime_listener(hass, SIGNAL_ADD_SENSOR, entry.entry_id, add_entity)
    )


class LoRaWANSensor(LoRaWANEntity, SensorEntity):
    """A LoRaWAN sensor entity."""

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        value = self.value
        if value is None:
            return None
        return state_value(value.value)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the assigned unit for this value."""
        return assign_value("sensor", self.device, self.value).unit

    @property
    def device_class(self) -> str | None:
        """Return the assigned sensor device class."""
        return assign_value("sensor", self.device, self.value).device_class

    @property
    def state_class(self) -> str | None:
        """Return the assigned state class."""
        return assign_value("sensor", self.device, self.value).state_class

    @property
    def entity_category(self) -> EntityCategory | None:
        """Mark raw payload sensors as diagnostic."""
        value = self.value
        if value and (value.key.startswith("raw_") or value.key.startswith("remaining_")):
            return EntityCategory.DIAGNOSTIC
        return None
