"""User-composed light entities for LoRaWAN devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .composite import LoRaWANCompositeEntity, configured_entities
from .const import CONF_DEVICE_LIGHT_ENTITIES, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]
    config = dict(entry.data)
    config.update(entry.options)
    async_add_entities(
        configured_entities(runtime, config, CONF_DEVICE_LIGHT_ENTITIES, LoRaWANLight)
    )


class LoRaWANLight(LoRaWANCompositeEntity, LightEntity):
    """A light assembled from LoRaWAN uplink and downlink entities."""

    def __init__(self, runtime, dev_eui: str, definition: dict[str, Any]) -> None:
        self._init_composite(runtime, dev_eui, definition, "light")
        self._attr_name = str(definition.get("name") or "Licht")
        self._optimistic_on: bool | None = None
        self._optimistic_brightness: int | None = None

    @property
    def is_on(self) -> bool | None:
        state = self._boolean("state_entity_id", "state_inverted")
        return state if state is not None else self._optimistic_on

    @property
    def brightness(self) -> int | None:
        value = self._number("brightness_entity_id")
        if value is None:
            return self._optimistic_brightness
        scale = max(1.0, float(self.definition.get("brightness_scale") or 100))
        return round(max(0, min(255, value * 255 / scale)))

    @property
    def supported_color_modes(self) -> set[ColorMode]:
        if self.definition.get("brightness_command_entity_id"):
            return {ColorMode.BRIGHTNESS}
        return {ColorMode.ONOFF}

    @property
    def color_mode(self) -> ColorMode:
        return (
            ColorMode.BRIGHTNESS
            if self.definition.get("brightness_command_entity_id")
            else ColorMode.ONOFF
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs and self.definition.get(
            "brightness_command_entity_id"
        ):
            brightness = int(kwargs[ATTR_BRIGHTNESS])
            scale = max(1.0, float(self.definition.get("brightness_scale") or 100))
            await self._async_set_number(
                "brightness_command_entity_id", brightness * scale / 255
            )
            self._optimistic_brightness = brightness
        await self._async_command("turn_on_command_entity_id", "on")
        self._optimistic_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._async_command("turn_off_command_entity_id", "off")
        self._optimistic_on = False
        self.async_write_ha_state()
