"""User-composed humidifier entities for LoRaWAN devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .composite import LoRaWANCompositeEntity, configured_entities
from .const import CONF_DEVICE_HUMIDIFIER_ENTITIES, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]
    config = dict(entry.data)
    config.update(entry.options)
    async_add_entities(
        configured_entities(
            runtime, config, CONF_DEVICE_HUMIDIFIER_ENTITIES, LoRaWANHumidifier
        )
    )


class LoRaWANHumidifier(LoRaWANCompositeEntity, HumidifierEntity):
    """A humidifier assembled from source entities."""

    def __init__(self, runtime, dev_eui: str, definition: dict[str, Any]) -> None:
        self._init_composite(runtime, dev_eui, definition, "humidifier")
        self._attr_name = str(definition.get("name") or "Luftbefeuchter")
        device_class = str(definition.get("device_class") or "humidifier")
        self._attr_device_class = (
            HumidifierDeviceClass(device_class)
            if device_class in {item.value for item in HumidifierDeviceClass}
            else HumidifierDeviceClass.HUMIDIFIER
        )
        self._optimistic_on: bool | None = None
        self._optimistic_target: float | None = None
        self._optimistic_mode: str | None = None

    @property
    def is_on(self) -> bool | None:
        state = self._boolean("state_entity_id", "state_inverted")
        return state if state is not None else self._optimistic_on

    @property
    def current_humidity(self) -> float | None:
        return self._number("current_humidity_entity_id")

    @property
    def target_humidity(self) -> float | None:
        state = self._number("target_humidity_state_entity_id")
        return state if state is not None else self._optimistic_target

    @property
    def min_humidity(self) -> float:
        return float(self.definition.get("min_humidity") or 0)

    @property
    def max_humidity(self) -> float:
        return float(self.definition.get("max_humidity") or 100)

    @property
    def mode(self) -> str | None:
        return (
            self._state("mode_state_entity_id")
            or self._optimistic_mode
            or next(iter(self.available_modes or []), None)
        )

    @property
    def available_modes(self) -> list[str] | None:
        options = self._options("mode_command_entity_id")
        return options or None

    @property
    def supported_features(self) -> HumidifierEntityFeature:
        return (
            HumidifierEntityFeature.MODES
            if self.definition.get("mode_command_entity_id")
            else HumidifierEntityFeature(0)
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._async_command("turn_on_command_entity_id", "on")
        self._optimistic_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_command("turn_off_command_entity_id", "off")
        self._optimistic_on = False
        self.async_write_ha_state()

    async def async_set_humidity(self, humidity: int) -> None:
        await self._async_set_number("target_humidity_command_entity_id", humidity)
        self._optimistic_target = float(humidity)
        self.async_write_ha_state()

    async def async_set_mode(self, mode: str) -> None:
        await self._async_select("mode_command_entity_id", mode)
        self._optimistic_mode = mode
        self.async_write_ha_state()
