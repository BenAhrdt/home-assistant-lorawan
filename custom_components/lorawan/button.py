"""Button controls for LoRaWAN button downlink parameters."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ADD_DOWNLINK_CONTROL, SIGNAL_DEVICE_ADDED, SIGNAL_REMOVE_DOWNLINK_CONTROL
from .downlink_entity import LoRaWANDownlinkEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]; added: set[str] = set()
    entities = {}
    @callback
    def add(key: str) -> None:
        if key not in added and (control := runtime.get_downlink_control(key)) and control["platform"] == "button":
            entity = LoRaWANDownlinkButton(runtime, key)
            added.add(key); entities[key] = entity; async_add_entities([entity])
    @callback
    def remove(key: str) -> None:
        added.discard(key)
        if (entity := entities.pop(key, None)) is not None: hass.async_create_task(entity.async_remove())
    for key in runtime.downlink_controls_for_platform("button"): add(key)
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_ADD_DOWNLINK_CONTROL, entry.entry_id, add))
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_REMOVE_DOWNLINK_CONTROL, entry.entry_id, remove))

    added_push_buttons: set[str] = set()

    @callback
    def add_push_button(dev_eui: str) -> None:
        if dev_eui in added_push_buttons or dev_eui not in runtime.devices:
            return
        added_push_buttons.add(dev_eui)
        async_add_entities([LoRaWANNextSendPushButton(runtime, dev_eui)])

    for dev_eui in runtime.devices:
        add_push_button(dev_eui)
    entry.async_on_unload(
        add_runtime_listener(hass, SIGNAL_DEVICE_ADDED, entry.entry_id, add_push_button)
    )


class LoRaWANDownlinkButton(LoRaWANDownlinkEntity, ButtonEntity):
    async def async_press(self) -> None: self._send(True)


class LoRaWANNextSendPushButton(ButtonEntity):
    """Send a queued downlink before the next uplink arrives."""

    _attr_has_entity_name = True
    _attr_name = "Next Send Push"
    _attr_icon = "mdi:send"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, runtime: LoRaWANRuntime, dev_eui: str) -> None:
        self.runtime = runtime
        self.dev_eui = dev_eui
        self._attr_unique_id = f"{runtime.entry.entry_id}_{dev_eui}_next_send_push"

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.dev_eui)}}

    async def async_press(self) -> None:
        self.runtime.push_queued_downlink(self.dev_eui)
