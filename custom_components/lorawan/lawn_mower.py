"""User-composed lawn mower entities for LoRaWAN devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lawn_mower import (
    LawnMowerActivity,
    LawnMowerEntity,
    LawnMowerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .composite import LoRaWANCompositeEntity, configured_entities
from .const import CONF_DEVICE_LAWN_MOWER_ENTITIES, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]
    config = dict(entry.data)
    config.update(entry.options)
    async_add_entities(
        configured_entities(
            runtime, config, CONF_DEVICE_LAWN_MOWER_ENTITIES, LoRaWANLawnMower
        )
    )


class LoRaWANLawnMower(LoRaWANCompositeEntity, LawnMowerEntity):
    """A lawn mower assembled from source entities."""

    def __init__(self, runtime, dev_eui: str, definition: dict[str, Any]) -> None:
        self._init_composite(runtime, dev_eui, definition, "lawn_mower")
        self._attr_name = str(definition.get("name") or "Mähroboter")
        self._optimistic_activity = LawnMowerActivity.DOCKED

    @property
    def activity(self) -> LawnMowerActivity:
        value = self._state("activity_entity_id")
        valid = {item.value: item for item in LawnMowerActivity}
        return valid.get(str(value).lower(), self._optimistic_activity)

    @property
    def supported_features(self) -> LawnMowerEntityFeature:
        features = LawnMowerEntityFeature(0)
        if self.definition.get("start_command_entity_id"):
            features |= LawnMowerEntityFeature.START_MOWING
        if self.definition.get("pause_command_entity_id"):
            features |= LawnMowerEntityFeature.PAUSE
        if self.definition.get("dock_command_entity_id"):
            features |= LawnMowerEntityFeature.DOCK
        return features

    async def async_start_mowing(self) -> None:
        await self._async_command("start_command_entity_id")
        self._optimistic_activity = LawnMowerActivity.MOWING
        self.async_write_ha_state()

    async def async_pause(self) -> None:
        await self._async_command("pause_command_entity_id")
        self._optimistic_activity = LawnMowerActivity.PAUSED
        self.async_write_ha_state()

    async def async_dock(self) -> None:
        await self._async_command("dock_command_entity_id")
        self._optimistic_activity = LawnMowerActivity.RETURNING
        self.async_write_ha_state()
