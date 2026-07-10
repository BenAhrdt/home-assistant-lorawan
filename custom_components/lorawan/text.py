"""Text controls for LoRaWAN ASCII and string downlink parameters."""

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ADD_DOWNLINK_CONTROL
from .downlink_entity import LoRaWANDownlinkEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]; added: set[str] = set()
    @callback
    def add(key: str) -> None:
        if key not in added and (control := runtime.get_downlink_control(key)) and control["platform"] == "text":
            added.add(key); async_add_entities([LoRaWANDownlinkText(runtime, key)])
    for key in runtime.downlink_controls_for_platform("text"): add(key)
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_ADD_DOWNLINK_CONTROL, entry.entry_id, add))


class LoRaWANDownlinkText(LoRaWANDownlinkEntity, TextEntity):
    async def async_set_value(self, value: str) -> None: self._send(value)
