"""Switch controls for LoRaWAN boolean downlink parameters."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, SIGNAL_ADD_DOWNLINK_CONTROL, SIGNAL_REMOVE_DOWNLINK_CONTROL
from .downlink_entity import LoRaWANDownlinkEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()
    entities = {}
    @callback
    def add(key: str) -> None:
        if key not in added and (control := runtime.get_downlink_control(key)) and control["platform"] == "switch":
            entity = LoRaWANDownlinkSwitch(runtime, key)
            added.add(key); entities[key] = entity; async_add_entities([entity])
    @callback
    def remove(key: str) -> None:
        added.discard(key)
        if (entity := entities.pop(key, None)) is not None: hass.async_create_task(entity.async_remove())
    for key in runtime.downlink_controls_for_platform("switch"): add(key)
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_ADD_DOWNLINK_CONTROL, entry.entry_id, add))
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_REMOVE_DOWNLINK_CONTROL, entry.entry_id, remove))


class LoRaWANDownlinkSwitch(LoRaWANDownlinkEntity, SwitchEntity, RestoreEntity):
    """An optimistic boolean downlink represented as a regular switch."""

    _attr_is_on = False

    async def async_added_to_hass(self) -> None:
        """Restore the displayed state without sending a downlink."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state in {"on", "off"}:
            self._attr_is_on = last_state.state == "on"

    async def async_turn_on(self, **kwargs) -> None:
        """Send the enabled state and optimistically update the switch."""
        self._send(True)
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Send the disabled state and optimistically update the switch."""
        self._send(False)
        self._attr_is_on = False
        self.async_write_ha_state()
