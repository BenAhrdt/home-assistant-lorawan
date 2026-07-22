"""User-composed cover entities for LoRaWAN devices."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval

from .const import CONF_DEVICE_COVER_ENTITIES, DOMAIN
from .runtime import LoRaWANRuntime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up manually composed cover entities."""
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    config = dict(entry.data)
    config.update(entry.options)
    entities = []
    for configured_dev_eui, definitions in (
        config.get(CONF_DEVICE_COVER_ENTITIES) or {}
    ).items():
        dev_eui = str(configured_dev_eui).replace(":", "").replace("-", "").upper()
        if isinstance(definitions, list):
            entities.extend(
                LoRaWANCover(runtime, dev_eui, definition)
                for definition in definitions
                if isinstance(definition, dict) and definition.get("id")
            )
    async_add_entities(entities)


class LoRaWANCover(CoverEntity):
    """A cover assembled from uplink states and downlink controls."""

    _attr_has_entity_name = True
    _attr_device_class = CoverDeviceClass.GARAGE

    def __init__(
        self, runtime: LoRaWANRuntime, dev_eui: str, definition: dict[str, Any]
    ) -> None:
        self.runtime = runtime
        self.dev_eui = dev_eui
        self.definition = definition
        self._attr_unique_id = (
            f"{runtime.entry.entry_id}_{dev_eui}_cover_{definition['id']}"
        )
        self._attr_name = str(definition.get("name") or "Tor")
        device_class = str(definition.get("device_class") or "garage")
        if device_class in {item.value for item in CoverDeviceClass}:
            self._attr_device_class = CoverDeviceClass(device_class)
        self._direction: str | None = None
        self._estimated_position: float | None = None
        self._target_position: float | None = None

    @property
    def device_info(self) -> DeviceInfo:
        return {"identifiers": {(DOMAIN, self.dev_eui)}}

    @property
    def available(self) -> bool:
        return self.runtime.is_device_online(self.dev_eui) and not (
            self._limit_active("closed_limit_entity_id", "closed_limit_inverted")
            and self._limit_active("open_limit_entity_id", "open_limit_inverted")
        )

    @property
    def assumed_state(self) -> bool:
        """Mark a state without a matching end switch or position as assumed."""
        return self._numeric_state("position_entity_id") is None and not (
            self._limit_active("closed_limit_entity_id", "closed_limit_inverted")
            or self._limit_active("open_limit_entity_id", "open_limit_inverted")
        )

    @property
    def is_closed(self) -> bool | None:
        if self._limit_active("closed_limit_entity_id", "closed_limit_inverted"):
            return True
        if self._limit_active("open_limit_entity_id", "open_limit_inverted"):
            return False
        position = self.current_cover_position
        if position is not None:
            return position == 0
        # HA treats "not at the closed end switch" as open for a one-switch setup.
        if self.definition.get("closed_limit_entity_id"):
            return False
        return None

    @property
    def is_opening(self) -> bool:
        return self._direction == "opening"

    @property
    def is_closing(self) -> bool:
        return self._direction == "closing"

    @property
    def current_cover_position(self) -> int | None:
        measured = self._numeric_state("position_entity_id")
        if measured is not None:
            return round(max(0, min(100, measured)))
        if self._limit_active("closed_limit_entity_id", "closed_limit_inverted"):
            return 0
        if self._limit_active("open_limit_entity_id", "open_limit_inverted"):
            return 100
        if self._has_travel_time() and self._estimated_position is not None:
            return round(max(0, min(100, self._estimated_position)))
        return None

    @property
    def supported_features(self) -> CoverEntityFeature:
        features = CoverEntityFeature(0)
        if self.definition.get("open_command_entity_id"):
            features |= CoverEntityFeature.OPEN
        if self.definition.get("close_command_entity_id"):
            features |= CoverEntityFeature.CLOSE
        if self.definition.get("stop_command_entity_id"):
            features |= CoverEntityFeature.STOP
        if self.definition.get("position_command_entity_id"):
            features |= CoverEntityFeature.SET_POSITION
        return features

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self._async_press("open_command_entity_id")
        self._start_moving("opening")

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self._async_press("close_command_entity_id")
        self._start_moving("closing")

    async def async_stop_cover(self, **kwargs: Any) -> None:
        await self._async_press("stop_command_entity_id")
        self._direction = None
        self._target_position = None
        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        position = int(kwargs[ATTR_POSITION])
        entity_id = self.definition.get("position_command_entity_id")
        if not entity_id:
            return
        await self.hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": position},
            blocking=True,
        )
        current = self.current_cover_position
        if current == position:
            self._direction = None
        else:
            self._direction = (
                "opening" if current is None or position > current else "closing"
            )
        if current is not None:
            self._estimated_position = float(current)
        self._target_position = float(position)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
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
        if self._has_travel_time():
            self.async_on_remove(
                async_track_time_interval(
                    self.hass,
                    self._async_estimate_position,
                    timedelta(seconds=1),
                )
            )

    @callback
    def _async_source_changed(self, event: Event) -> None:
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")
        if entity_id in {
            self.definition.get("closed_limit_entity_id"),
            self.definition.get("open_limit_entity_id"),
        } and (
            new_state is None
            or new_state.state in {"unknown", "unavailable"}
            or old_state is None
            or old_state.state in {"unknown", "unavailable"}
        ):
            self.async_write_ha_state()
            return
        active_now = new_state is not None and new_state.state == STATE_ON
        active_before = old_state is not None and old_state.state == STATE_ON
        if self.definition.get("closed_limit_inverted"):
            active_now, active_before = not active_now, not active_before
        if entity_id == self.definition.get("closed_limit_entity_id"):
            if active_now:
                self._estimated_position, self._direction = 0.0, None
                self._target_position = None
            elif active_before:
                self._start_moving("opening")
        active_now = new_state is not None and new_state.state == STATE_ON
        active_before = old_state is not None and old_state.state == STATE_ON
        if self.definition.get("open_limit_inverted"):
            active_now, active_before = not active_now, not active_before
        if entity_id == self.definition.get("open_limit_entity_id"):
            if active_now:
                self._estimated_position, self._direction = 100.0, None
                self._target_position = None
            elif active_before:
                self._start_moving("closing")
        self.async_write_ha_state()

    @callback
    def _async_estimate_position(self, _now) -> None:
        if not self._direction:
            return
        if self._estimated_position is None:
            self._estimated_position = 0.0 if self._direction == "opening" else 100.0
        duration = self._travel_time(self._direction)
        delta = 100.0 / duration
        self._estimated_position += delta if self._direction == "opening" else -delta
        reached_target = self._target_position is not None and (
            (
                self._direction == "opening"
                and self._estimated_position >= self._target_position
            )
            or (
                self._direction == "closing"
                and self._estimated_position <= self._target_position
            )
        )
        if reached_target:
            self._estimated_position = self._target_position
            self._target_position = None
            self._direction = None
        elif self._estimated_position <= 0 or self._estimated_position >= 100:
            self._estimated_position = max(0.0, min(100.0, self._estimated_position))
            self._target_position = None
            self._direction = None
        self.async_write_ha_state()

    def _start_moving(self, direction: str) -> None:
        current = self.current_cover_position
        if current is not None:
            self._estimated_position = float(current)
        self._target_position = None
        self._direction = direction
        self.async_write_ha_state()

    async def _async_press(self, key: str) -> None:
        entity_id = self.definition.get(key)
        if not entity_id:
            return
        domain = entity_id.partition(".")[0]
        service = "press" if domain == "button" else "turn_on"
        await self.hass.services.async_call(
            domain, service, {"entity_id": entity_id}, blocking=True
        )

    def _limit_active(self, key: str, invert_key: str) -> bool:
        entity_id = self.definition.get(key)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or state.state in {"unknown", "unavailable"}:
            return False
        active = state.state == STATE_ON
        return not active if self.definition.get(invert_key) else active

    def _numeric_state(self, key: str) -> float | None:
        entity_id = self.definition.get(key)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or state.state in {"unknown", "unavailable"}:
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

    def _travel_time(self, direction: str) -> float:
        key = "open_travel_time" if direction == "opening" else "close_travel_time"
        try:
            return max(1.0, float(self.definition.get(key) or 0))
        except (TypeError, ValueError):
            return 1.0

    def _has_travel_time(self) -> bool:
        for key in ("open_travel_time", "close_travel_time"):
            try:
                if float(self.definition.get(key) or 0) > 0:
                    return True
            except (TypeError, ValueError):
                pass
        return False
