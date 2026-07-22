"""Shared helpers for user-composed LoRaWAN entities."""

from __future__ import annotations

from typing import Any

from homeassistant.const import STATE_ON
from homeassistant.core import Event, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN


class LoRaWANCompositeEntity:
    """Mixin that connects a composed entity to source entities."""

    _attr_has_entity_name = True

    def _init_composite(self, runtime, dev_eui: str, definition: dict, domain: str) -> None:
        self.runtime = runtime
        self.dev_eui = dev_eui
        self.definition = definition
        self._attr_unique_id = (
            f"{runtime.entry.entry_id}_{dev_eui}_{domain}_{definition['id']}"
        )

    @property
    def device_info(self) -> DeviceInfo:
        return {"identifiers": {(DOMAIN, self.dev_eui)}}

    @property
    def available(self) -> bool:
        return self.runtime.is_device_online(self.dev_eui)

    async def async_added_to_hass(self) -> None:
        entity_ids = {
            value
            for key, value in self.definition.items()
            if key.endswith("_entity_id") and isinstance(value, str) and value
        }
        if entity_ids:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, entity_ids, self._async_composite_source_changed
                )
            )

    @callback
    def _async_composite_source_changed(self, _event: Event) -> None:
        self.async_write_ha_state()

    def _state(self, key: str) -> str | None:
        entity_id = self.definition.get(key)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        return state.state

    def _number(self, key: str) -> float | None:
        value = self._state(key)
        try:
            return float(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def _boolean(self, key: str, invert_key: str | None = None) -> bool | None:
        value = self._state(key)
        if value is None:
            return None
        active = value == STATE_ON
        return not active if invert_key and self.definition.get(invert_key) else active

    def _options(self, key: str) -> list[str]:
        entity_id = self.definition.get(key)
        state = self.hass.states.get(entity_id) if entity_id else None
        return list(state.attributes.get("options", [])) if state else []

    async def _async_command(self, key: str, action: str = "on") -> None:
        entity_id = self.definition.get(key)
        if not entity_id:
            return
        domain = entity_id.partition(".")[0]
        if domain == "button":
            service = "press"
        else:
            service = "turn_off" if action == "off" else "turn_on"
        await self.hass.services.async_call(
            domain, service, {"entity_id": entity_id}, blocking=True
        )

    async def _async_set_number(self, key: str, value: float) -> None:
        entity_id = self.definition.get(key)
        if entity_id:
            await self.hass.services.async_call(
                "number",
                "set_value",
                {"entity_id": entity_id, "value": value},
                blocking=True,
            )

    async def _async_select(self, key: str, option: str) -> None:
        entity_id = self.definition.get(key)
        if entity_id:
            await self.hass.services.async_call(
                "select",
                "select_option",
                {"entity_id": entity_id, "option": option},
                blocking=True,
            )


def configured_entities(runtime, config: dict[str, Any], config_key: str, cls):
    """Create composed entities from all per-device definitions."""
    entities = []
    for configured_dev_eui, definitions in (config.get(config_key) or {}).items():
        dev_eui = str(configured_dev_eui).replace(":", "").replace("-", "").upper()
        if isinstance(definitions, list):
            entities.extend(
                cls(runtime, dev_eui, definition)
                for definition in definitions
                if isinstance(definition, dict) and definition.get("id")
            )
    return entities
