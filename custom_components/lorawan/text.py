"""Text controls for LoRaWAN ASCII and string downlink parameters."""

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    DOMAIN,
    SIGNAL_ADD_DOWNLINK_CONTROL,
    SIGNAL_DEVICE_ADDED,
    SIGNAL_REMOVE_DOWNLINK_CONTROL,
    SIGNAL_UPDATE_DOWNLINK_CONTROLS,
)
from .downlink_entity import LoRaWANDownlinkEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]; added: set[str] = set()
    entities = {}
    @callback
    def add(key: str) -> None:
        if key not in added and (control := runtime.get_downlink_control(key)) and control["platform"] == "text":
            entity = LoRaWANDownlinkText(runtime, key)
            added.add(key); entities[key] = entity; async_add_entities([entity])
    @callback
    def remove(key: str) -> None:
        added.discard(key)
        if (entity := entities.pop(key, None)) is not None: hass.async_create_task(entity.async_remove())
    for key in runtime.downlink_controls_for_platform("text"): add(key)
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_ADD_DOWNLINK_CONTROL, entry.entry_id, add))
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_REMOVE_DOWNLINK_CONTROL, entry.entry_id, remove))

    added_device_types: set[str] = set()

    @callback
    def add_device_type(dev_eui: str) -> None:
        if dev_eui in added_device_types or dev_eui not in runtime.devices:
            return
        added_device_types.add(dev_eui)
        async_add_entities([LoRaWANDeviceTypeText(runtime, dev_eui)])

    for dev_eui in runtime.devices:
        add_device_type(dev_eui)
    entry.async_on_unload(
        add_runtime_listener(hass, SIGNAL_DEVICE_ADDED, entry.entry_id, add_device_type)
    )


class LoRaWANDownlinkText(LoRaWANDownlinkEntity, TextEntity):
    _attr_native_value = ""

    async def async_set_value(self, value: str) -> None:
        self._send(value)
        self._attr_native_value = value
        self.async_write_ha_state()


class LoRaWANDeviceTypeText(TextEntity):
    """Editable device type used to select the best downlink profile."""

    _attr_has_entity_name = True
    _attr_name = "Gerätetyp"
    _attr_native_min = 0
    _attr_native_max = 255
    _attr_icon = "mdi:devices"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, runtime: LoRaWANRuntime, dev_eui: str) -> None:
        self.runtime = runtime
        self.dev_eui = dev_eui
        self._attr_unique_id = f"{runtime.entry.entry_id}_{dev_eui}_device_type"

    @property
    def native_value(self) -> str:
        device = self.runtime.devices.get(self.dev_eui)
        return str(device.device_type or "") if device else ""

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, self.dev_eui)}}

    async def async_set_value(self, value: str) -> None:
        self.runtime.set_device_type(self.dev_eui, value)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_UPDATE_DOWNLINK_CONTROLS,
                self._async_update_device_type,
            )
        )

    @callback
    def _async_update_device_type(self) -> None:
        self.async_write_ha_state()
