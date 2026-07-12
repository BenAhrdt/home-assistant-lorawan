"""User-composed climate entities for LoRaWAN devices."""

from __future__ import annotations

from typing import Any
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import CONF_DEVICE_CLIMATE_ENTITIES, DOMAIN
from .runtime import LoRaWANRuntime

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up manually composed climate entities."""
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    config = dict(entry.data)
    config.update(entry.options)
    entities: list[LoRaWANClimate] = []
    for configured_dev_eui, definitions in (config.get(CONF_DEVICE_CLIMATE_ENTITIES) or {}).items():
        dev_eui = str(configured_dev_eui).replace(":", "").replace("-", "").upper()
        if not isinstance(definitions, list):
            continue
        for definition in definitions:
            if isinstance(definition, dict) and definition.get("id"):
                entities.append(LoRaWANClimate(runtime, dev_eui, definition))
    _LOGGER.debug("Setting up %d composed LoRaWAN climate entities", len(entities))
    async_add_entities(entities)


class LoRaWANClimate(ClimateEntity):
    """A climate entity assembled from uplink and downlink entities."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self, runtime: LoRaWANRuntime, dev_eui: str, definition: dict[str, Any]
    ) -> None:
        self.runtime = runtime
        self.dev_eui = dev_eui
        self.definition = definition
        self._attr_unique_id = (
            f"{runtime.entry.entry_id}_{dev_eui}_climate_{definition['id']}"
        )
        self._attr_name = str(definition.get("name") or "Thermostat")
        self._optimistic_target: float | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Attach the entity to its LoRaWAN device."""
        return {"identifiers": {(DOMAIN, self.dev_eui)}}

    @property
    def available(self) -> bool:
        """Use the device's uplink timeout as availability."""
        return self.runtime.is_device_online(self.dev_eui)

    @property
    def current_temperature(self) -> float | None:
        """Return the assigned current-temperature uplink."""
        return self._numeric_state("current_temperature_entity_id")

    @property
    def target_temperature(self) -> float | None:
        """Return confirmed or optimistic target temperature."""
        confirmed = self._numeric_state("target_temperature_state_entity_id")
        return confirmed if confirmed is not None else self._optimistic_target

    @property
    def hvac_mode(self) -> HVACMode:
        """Return an assigned mode when it maps to a native HA HVAC mode."""
        entity_id = self.definition.get("hvac_mode_state_entity_id")
        state = self.hass.states.get(entity_id) if entity_id else None
        if state and state.state in {mode.value for mode in HVACMode}:
            return HVACMode(state.state)
        return HVACMode.HEAT

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Expose assigned native HA modes, or a fixed heat mode."""
        state = self._command_state("hvac_mode_command_entity_id")
        options = state.attributes.get("options", []) if state else []
        modes = [HVACMode(option) for option in options if option in {mode.value for mode in HVACMode}]
        if state and state.entity_id.partition(".")[0] == "switch":
            modes = [HVACMode.OFF, HVACMode.HEAT]
        state_entity_id = self.definition.get("hvac_mode_state_entity_id")
        state_value = self.hass.states.get(state_entity_id) if state_entity_id else None
        if state_value and state_value.state == HVACMode.OFF.value and HVACMode.OFF not in modes:
            modes.insert(0, HVACMode.OFF)
        return modes or [HVACMode.HEAT]

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Expose only controls that were actually assigned."""
        features = ClimateEntityFeature(0)
        if self.definition.get("target_temperature_command_entity_id"):
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        return features

    @property
    def min_temp(self) -> float:
        """Take the range from the assigned number downlink when available."""
        state = self._command_state("target_temperature_command_entity_id")
        return float(state.attributes.get("min", 7)) if state else 7

    @property
    def max_temp(self) -> float:
        """Take the range from the assigned number downlink when available."""
        state = self._command_state("target_temperature_command_entity_id")
        return float(state.attributes.get("max", 35)) if state else 35

    @property
    def target_temperature_step(self) -> float:
        """Take the step from the assigned number downlink when available."""
        state = self._command_state("target_temperature_command_entity_id")
        return float(state.attributes.get("step", 0.5)) if state else 0.5

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Forward a target-temperature change to the assigned downlink entity."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        entity_id = self.definition.get("target_temperature_command_entity_id")
        if temperature is None or not entity_id:
            return
        await self.hass.services.async_call(
            "number", "set_value", {"entity_id": entity_id, "value": temperature}, blocking=True
        )
        self._optimistic_target = float(temperature)
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Forward a mode change to an optional select or switch downlink."""
        entity_id = self.definition.get("hvac_mode_command_entity_id")
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None:
            return
        domain = state.entity_id.partition(".")[0]
        if domain == "select":
            await self.hass.services.async_call(
                "select", "select_option",
                {"entity_id": entity_id, "option": hvac_mode.value}, blocking=True,
            )
        elif domain == "switch":
            service = "turn_off" if hvac_mode == HVACMode.OFF else "turn_on"
            await self.hass.services.async_call(
                "switch", service, {"entity_id": entity_id}, blocking=True
            )

    async def async_added_to_hass(self) -> None:
        """Track each assigned source entity."""
        entity_ids = {
            value
            for key, value in self.definition.items()
            if key.endswith("_entity_id") and isinstance(value, str) and value
        }
        if entity_ids:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, entity_ids, self._async_source_changed
                )
            )

    @callback
    def _async_source_changed(self, event: Event) -> None:
        """Publish an updated composed state."""
        if event.data.get("entity_id") == self.definition.get(
            "target_temperature_state_entity_id"
        ):
            self._optimistic_target = None
        self.async_write_ha_state()

    def _numeric_state(self, key: str) -> float | None:
        entity_id = self.definition.get(key)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _command_state(self, key: str):
        entity_id = self.definition.get(key)
        return self.hass.states.get(entity_id) if entity_id else None
