"""Assign Home Assistant semantics to LoRaWAN payload values."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from .models import LoRaWANDevice, LoRaWANValue


@dataclass(frozen=True, slots=True)
class EntityAssignment:
    """Home Assistant metadata assigned to one payload value."""

    device_class: str | None = None
    state_class: str | None = None
    unit: str | None = None


@dataclass(frozen=True, slots=True)
class AssignmentRule:
    """One exact-name rule for assigning Home Assistant semantics."""

    names: tuple[str, ...]
    device_class: str | None = None
    state_class: str | None = None
    unit: str | None = None
    platforms: tuple[str, ...] = ("sensor", "binary_sensor")
    value_types: tuple[type, ...] = (bool, int, float, str)
    stop_fallback: bool = False

    def matches(
        self, platform: str, identifiers: frozenset[str], value: Any
    ) -> bool:
        """Return true if this rule matches a value's own field name."""
        return (
            platform in self.platforms
            and isinstance(value, self.value_types)
            and not (isinstance(value, bool) and bool not in self.value_types)
            and any(_normalize_name(name) in identifiers for name in self.names)
        )


NUMERIC = (int, float)
SENSOR = ("sensor",)
BINARY_SENSOR = ("binary_sensor",)

# These rules deliberately match the value's own key only. Device model, device
# name and application name must not leak semantics into every value of a device.
DEFAULT_ASSIGNMENT_RULES: tuple[AssignmentRule, ...] = (
    AssignmentRule(("AbsoluteHumidity",), None, "measurement", "g/m³", SENSOR, NUMERIC),
    AssignmentRule(("Hum_SHT", "Humidity", "RelativeHumidity"), "humidity", "measurement", "%", SENSOR, NUMERIC),
    AssignmentRule(("DewPointTemperature", "ExternalTemperature", "ExtSensorTemperature", "SensorTemperature", "Soiltemperature", "TargetTemperature", "TargetTemperatureFloat", "TempC_SHT", "Temperatur", "Temperature", "room_temperature", "heating_control.room_temperature.value"), "temperature", "measurement", "°C", SENSOR, NUMERIC),
    AssignmentRule(("battery_voltage.value",), "voltage", "measurement", "mV", SENSOR, NUMERIC),
    AssignmentRule(("BatteryPercent", "battery_percent", "battery_level"), "battery", "measurement", "%", SENSOR, NUMERIC),
    AssignmentRule(("Battery", "BatteryVoltage", "batteryVoltage", "BatV", "LoRa_Voltage", "Supply_Voltage", "Volt", "Voltage"), "voltage", "measurement", "V", SENSOR, NUMERIC),
    AssignmentRule(("Gustspeed", "Windspeed"), "wind_speed", "measurement", "m/s", SENSOR, NUMERIC),
    AssignmentRule(("Winddirection",), "wind_direction", "measurement", "°", SENSOR, NUMERIC),
    AssignmentRule(("Light", "Illuminance", "Brightness"), "illuminance", "measurement", "lx", SENSOR, NUMERIC),
    AssignmentRule(("Liter",), "volume", "measurement", "L", SENSOR, NUMERIC),
    AssignmentRule(("MotorPosition", "MotorRange"), None, "measurement", "INC", SENSOR, NUMERIC),
    AssignmentRule(("ValveOpenness", "Percent"), None, "measurement", "%", SENSOR, NUMERIC),
    AssignmentRule(("Pressure",), "pressure", "measurement", "mbar", SENSOR, NUMERIC),
    AssignmentRule(("Rainfall",), "precipitation", "measurement", "mm", SENSOR, NUMERIC),
    AssignmentRule(("Soilconductivity",), "conductivity", "measurement", "µS/cm", SENSOR, NUMERIC),
    AssignmentRule(("Soilmoisture",), None, "measurement", "vol-%", SENSOR, NUMERIC),
    AssignmentRule(("SoilNitrogen", "SoilPhosphorus", "SoilPotassium"), None, "measurement", "mg/kg", SENSOR, NUMERIC),
    AssignmentRule(("SoilPH",), "ph", "measurement", None, SENSOR, NUMERIC),
    AssignmentRule(("Weight",), "weight", "measurement", "kg", SENSOR, NUMERIC),
    AssignmentRule(("WeightGramm",), "weight", "measurement", "g", SENSOR, NUMERIC),
    AssignmentRule(("Uvi",), None, "measurement", None, SENSOR, NUMERIC),
    AssignmentRule(("KeepAliveTime",), "duration", "measurement", "min", SENSOR, NUMERIC),
    AssignmentRule(("LastOpenDuration", "Duration"), "duration", "measurement", "s", SENSOR, NUMERIC),
    AssignmentRule(("OpenTimes", "Counter", "Count"), None, "total_increasing", None, SENSOR, NUMERIC),
    AssignmentRule(("Current",), "current", "measurement", "A", SENSOR, NUMERIC),
    AssignmentRule(("Power",), "power", "measurement", "W", SENSOR, NUMERIC),
    AssignmentRule(("Energy",), "energy", "total_increasing", "kWh", SENSOR, NUMERIC),
    AssignmentRule(("CO2", "PM", "TVOC"), None, "measurement", "ppm", SENSOR, NUMERIC),
    AssignmentRule(("Alarm", "BrokenSensor", "CalibrationFailed", "LowBat", "NotAttachedBackplate", "Mode", "Mod", "DeviceType", "StateText", "Timestamp"), None, None, None, SENSOR, (int, float, str), True),
    AssignmentRule(("DeviceOnline",), "connectivity", None, None, BINARY_SENSOR, (bool,)),
    AssignmentRule(("OpenWindow", "WindowOpen"), "window", None, None, BINARY_SENSOR),
    AssignmentRule(("DoorOpen", "OpenDoor"), "door", None, None, BINARY_SENSOR),
    AssignmentRule(("Contact", "Open", "Opened"), "opening", None, None, BINARY_SENSOR),
    AssignmentRule(("Motion", "PIR", "Occupied"), "motion", None, None, BINARY_SENSOR),
    AssignmentRule(("LowBat", "battery_low"), "battery", None, None, BINARY_SENSOR),
    AssignmentRule(("Tamper",), "tamper", None, None, BINARY_SENSOR),
    AssignmentRule(("WaterLeakStatus",), "moisture", None, None, BINARY_SENSOR),
    AssignmentRule(("Alarm", "Error", "Failed", "BrokenSensor", "CalibrationFailed", "NotAttachedBackplate"), "problem", None, None, BINARY_SENSOR),
)


def assign_value(
    platform: str,
    device: LoRaWANDevice | None,
    value: LoRaWANValue | None,
) -> EntityAssignment:
    """Return Home Assistant metadata for one entity value."""
    del device  # Semantics belong to the value, never to its parent device name.
    if value is None:
        return EntityAssignment()
    if value.key.startswith(("raw_", "remaining_", "downlink_")):
        return EntityAssignment()

    identifiers = _assignment_identifiers(value)
    for rule in DEFAULT_ASSIGNMENT_RULES:
        if rule.matches(platform, identifiers, value.value):
            if rule.stop_fallback:
                return EntityAssignment()
            return EntityAssignment(rule.device_class, rule.state_class, rule.unit)

    # ioBroker's subAssign uses a contains match only for weight variants.
    leaf = _normalize_name(value.raw_key.rsplit(".", 1)[-1])
    if platform == "sensor" and isinstance(value.value, NUMERIC):
        if "weightgramm" in leaf:
            return EntityAssignment("weight", "measurement", "g")
        if "weight" in leaf:
            return EntityAssignment("weight", "measurement", "kg")
        return EntityAssignment(state_class="measurement")
    return EntityAssignment()


def _assignment_identifiers(value: LoRaWANValue) -> frozenset[str]:
    """Return normalized exact identifiers for one payload field."""
    raw_leaf = value.raw_key.rsplit(".", 1)[-1]
    key_leaf = value.key.rsplit("_", 1)[-1]
    return frozenset(
        _normalize_name(item)
        for item in (value.raw_key, raw_leaf, value.key, key_leaf, value.name)
        if item
    )


def _normalize_name(value: str) -> str:
    """Normalize field names without turning them into substring matches."""
    return re.sub(r"[^a-z0-9]+", "", value.casefold())
