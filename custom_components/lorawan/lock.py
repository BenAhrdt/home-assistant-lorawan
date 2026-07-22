"""User-composed lock entities for LoRaWAN devices."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .composite import LoRaWANCompositeEntity, configured_entities
from .const import CONF_DEVICE_LOCK_ENTITIES, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]
    config = dict(entry.data)
    config.update(entry.options)
    async_add_entities(
        configured_entities(runtime, config, CONF_DEVICE_LOCK_ENTITIES, LoRaWANLock)
    )


class LoRaWANLock(LoRaWANCompositeEntity, LockEntity):
    """A lock assembled from source entities."""

    def __init__(self, runtime, dev_eui: str, definition: dict[str, Any]) -> None:
        self._init_composite(runtime, dev_eui, definition, "lock")
        self._attr_name = str(definition.get("name") or "Schloss")
        self._optimistic_locked: bool | None = None

    @property
    def is_locked(self) -> bool | None:
        state = self._boolean("locked_state_entity_id", "locked_state_inverted")
        return state if state is not None else self._optimistic_locked

    @property
    def supported_features(self) -> LockEntityFeature:
        return (
            LockEntityFeature.OPEN
            if self.definition.get("open_command_entity_id")
            else LockEntityFeature(0)
        )

    async def async_lock(self, **kwargs: Any) -> None:
        await self._async_command("lock_command_entity_id", "on")
        self._optimistic_locked = True
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        await self._async_command("unlock_command_entity_id", "off")
        self._optimistic_locked = False
        self.async_write_ha_state()

    async def async_open(self, **kwargs: Any) -> None:
        await self._async_command("open_command_entity_id", "on")
