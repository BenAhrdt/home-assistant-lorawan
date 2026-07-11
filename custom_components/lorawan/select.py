"""Select controls for enumerated LoRaWAN downlink parameters."""

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ADD_DOWNLINK_CONTROL, SIGNAL_REMOVE_DOWNLINK_CONTROL
from .downlink_entity import LoRaWANDownlinkEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enumerated downlink selects."""
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()
    entities: dict[str, LoRaWANDownlinkSelect] = {}

    @callback
    def add(key: str) -> None:
        control = runtime.get_downlink_control(key)
        if key in added or control is None or control["platform"] != "select":
            return
        entity = LoRaWANDownlinkSelect(runtime, key)
        added.add(key)
        entities[key] = entity
        async_add_entities([entity])

    @callback
    def remove(key: str) -> None:
        added.discard(key)
        if (entity := entities.pop(key, None)) is not None:
            hass.async_create_task(entity.async_remove())

    for key in runtime.downlink_controls_for_platform("select"):
        add(key)
    entry.async_on_unload(
        add_runtime_listener(hass, SIGNAL_ADD_DOWNLINK_CONTROL, entry.entry_id, add)
    )
    entry.async_on_unload(
        add_runtime_listener(hass, SIGNAL_REMOVE_DOWNLINK_CONTROL, entry.entry_id, remove)
    )


class LoRaWANDownlinkSelect(LoRaWANDownlinkEntity, SelectEntity):
    """Choose a labelled state and send its raw numeric value."""

    _attr_current_option = None

    @property
    def options(self) -> list[str]:
        """Return the human-readable options."""
        return list(self.control["state_options"].values())

    async def async_select_option(self, option: str) -> None:
        """Send the raw value belonging to a selected label."""
        states = self.control["state_options"]
        raw_value = next(
            (raw for raw, label in states.items() if label == option),
            None,
        )
        if raw_value is None:
            raise ValueError(f"Unbekannte Auswahl: {option}")
        self._send(raw_value)
        self._attr_current_option = option
        self.async_write_ha_state()
