"""Number controls for LoRaWAN downlink parameters."""

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_ADD_DOWNLINK_CONTROL, SIGNAL_REMOVE_DOWNLINK_CONTROL
from .downlink_entity import LoRaWANDownlinkEntity
from .runtime import LoRaWANRuntime, add_runtime_listener


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    runtime: LoRaWANRuntime = hass.data[DOMAIN][entry.entry_id]
    added: set[str] = set()
    entities = {}

    @callback
    def add(key: str) -> None:
        if key not in added and (control := runtime.get_downlink_control(key)) and control["platform"] == "number":
            entity = LoRaWANDownlinkNumber(runtime, key)
            added.add(key); entities[key] = entity; async_add_entities([entity])
    @callback
    def remove(key: str) -> None:
        added.discard(key)
        if (entity := entities.pop(key, None)) is not None: hass.async_create_task(entity.async_remove())

    for key in runtime.downlink_controls_for_platform("number"):
        add(key)
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_ADD_DOWNLINK_CONTROL, entry.entry_id, add))
    entry.async_on_unload(add_runtime_listener(hass, SIGNAL_REMOVE_DOWNLINK_CONTROL, entry.entry_id, remove))


class LoRaWANDownlinkNumber(LoRaWANDownlinkEntity, NumberEntity):
    _attr_mode = NumberMode.BOX
    _attr_native_value = 0

    @property
    def native_min_value(self) -> float:
        parameter = self.control["parameter"]
        value = float(parameter.get("limitMinValue", 0)) if parameter.get("limitMin") else -1_000_000
        return self._normalized_value(value)

    @property
    def native_max_value(self) -> float:
        parameter = self.control["parameter"]
        value = float(parameter.get("limitMaxValue", 0)) if parameter.get("limitMax") else 1_000_000
        return self._normalized_value(value)

    @property
    def native_step(self) -> float:
        decimal_places = self._decimal_places
        return 1 if decimal_places == 0 else 10 ** -decimal_places

    @property
    def native_unit_of_measurement(self) -> str | None:
        return self.control["parameter"].get("unit") or None

    async def async_set_native_value(self, value: float) -> None:
        normalized = self._normalized_value(value)
        if abs(float(value) - float(normalized)) > 1e-9:
            raise ValueError(
                f"Der Wert darf höchstens {self._decimal_places} Dezimalstellen haben"
            )
        self._send(normalized)
        self._attr_native_value = normalized
        self.async_write_ha_state()

    @property
    def _decimal_places(self) -> int:
        return max(0, int(self.control["parameter"].get("decimalPlaces", 0)))

    def _normalized_value(self, value: float) -> int | float:
        decimal_places = self._decimal_places
        if decimal_places == 0:
            return int(round(float(value)))
        return round(float(value), decimal_places)
