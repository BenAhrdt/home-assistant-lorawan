"""Number controls for LoRaWAN downlink parameters."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ADD_DOWNLINK_CONTROL
from .downlink_entity import LoRaWANDownlinkEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()

    @callback
    def add(key: str) -> None:
        if key not in added and (control := runtime.get_downlink_control(key)) and control["platform"] == "number":
            added.add(key)
            async_add_entities([LoRaWANDownlinkNumber(runtime, key)])

    for key in runtime.downlink_controls_for_platform("number"):
        add(key)
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_ADD_DOWNLINK_CONTROL, entry.entry_id, add))


class LoRaWANDownlinkNumber(LoRaWANDownlinkEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    @property
    def native_min_value(self) -> float:
        parameter = self.control["parameter"]
        return float(parameter.get("limitMinValue", 0)) if parameter.get("limitMin") else -1_000_000

    @property
    def native_max_value(self) -> float:
        parameter = self.control["parameter"]
        return float(parameter.get("limitMaxValue", 0)) if parameter.get("limitMax") else 1_000_000

    @property
    def native_step(self) -> float:
        return 10 ** -int(self.control["parameter"].get("decimalPlaces", 0))

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self.control["parameter"].get("unit") or None

    async def async_set_native_value(self, value: float) -> None:
        self._send(value)
