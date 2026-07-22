"""User-composed vacuum entities for LoRaWAN devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .composite import LoRaWANCompositeEntity, configured_entities
from .const import CONF_DEVICE_VACUUM_ENTITIES, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]
    config = dict(entry.data)
    config.update(entry.options)
    async_add_entities(
        configured_entities(runtime, config, CONF_DEVICE_VACUUM_ENTITIES, LoRaWANVacuum)
    )


class LoRaWANVacuum(LoRaWANCompositeEntity, StateVacuumEntity):
    """A vacuum assembled from source entities."""

    def __init__(self, runtime, dev_eui: str, definition: dict[str, Any]) -> None:
        self._init_composite(runtime, dev_eui, definition, "vacuum")
        self._attr_name = str(definition.get("name") or "Saugroboter")
        self._optimistic_activity = VacuumActivity.IDLE
        self._optimistic_fan_speed: str | None = None

    @property
    def activity(self) -> VacuumActivity:
        value = self._state("activity_entity_id")
        valid = {item.value: item for item in VacuumActivity}
        return valid.get(str(value).lower(), self._optimistic_activity)

    @property
    def fan_speed(self) -> str | None:
        return self._state("fan_speed_state_entity_id") or self._optimistic_fan_speed

    @property
    def fan_speed_list(self) -> list[str]:
        return self._options("fan_speed_command_entity_id")

    @property
    def supported_features(self) -> VacuumEntityFeature:
        features = VacuumEntityFeature.STATE
        mapping = {
            "start_command_entity_id": VacuumEntityFeature.START,
            "pause_command_entity_id": VacuumEntityFeature.PAUSE,
            "stop_command_entity_id": VacuumEntityFeature.STOP,
            "return_command_entity_id": VacuumEntityFeature.RETURN_HOME,
            "fan_speed_command_entity_id": VacuumEntityFeature.FAN_SPEED,
        }
        for key, feature in mapping.items():
            if self.definition.get(key):
                features |= feature
        return features

    async def async_start(self) -> None:
        await self._async_command("start_command_entity_id")
        self._optimistic_activity = VacuumActivity.CLEANING
        self.async_write_ha_state()

    async def async_pause(self) -> None:
        await self._async_command("pause_command_entity_id")
        self._optimistic_activity = VacuumActivity.PAUSED
        self.async_write_ha_state()

    async def async_stop(self, **kwargs: Any) -> None:
        await self._async_command("stop_command_entity_id")
        self._optimistic_activity = VacuumActivity.IDLE
        self.async_write_ha_state()

    async def async_return_to_base(self, **kwargs: Any) -> None:
        await self._async_command("return_command_entity_id")
        self._optimistic_activity = VacuumActivity.RETURNING
        self.async_write_ha_state()

    async def async_set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        await self._async_select("fan_speed_command_entity_id", fan_speed)
        self._optimistic_fan_speed = fan_speed
        self.async_write_ha_state()
