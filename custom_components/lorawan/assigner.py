"""Assign Home Assistant semantics to LoRaWAN payload values."""

from __future__ import annotations

from dataclasses import dataclass
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
    """One rule for assigning Home Assistant semantics."""

    contains: tuple[str, ...]
    device_class: str | None = None
    state_class: str | None = None
    unit: str | None = None
    platforms: tuple[str, ...] = ("sensor", "binary_sensor")
    value_types: tuple[type, ...] = (bool, int, float, str)
    stop_fallback: bool = False

    def matches(self, platform: str, haystack: str, value: Any) -> bool:
        """Return true if this rule matches a value."""
        return (
            platform in self.platforms
            and isinstance(value, self.value_types)
            and any(needle in haystack for needle in self.contains)
        )


DEFAULT_ASSIGNMENT_RULES: tuple[AssignmentRule, ...] = (
    AssignmentRule(("temperature", "temperatur", "extsensortemperature"), "temperature", "measurement", "°C", ("sensor",), (int, float)),
    AssignmentRule(("humidity", "feuchte"), "humidity", "measurement", "%", ("sensor",), (int, float)),
    AssignmentRule(("batterypercent", "battery_percent", "battery_level"), "battery", "measurement", "%", ("sensor",), (int, float)),
    AssignmentRule(("batteryvoltage", "batv", "voltage"), "voltage", "measurement", "V", ("sensor",), (int, float)),
    AssignmentRule(("lastopenduration", "duration"), "duration", "measurement", "s", ("sensor",), (int, float)),
    AssignmentRule(("opentimes", "counter", "count"), None, "total_increasing", None, ("sensor",), (int, float)),
    AssignmentRule(("current",), "current", "measurement", "A", ("sensor",), (int, float)),
    AssignmentRule(("power",), "power", "measurement", "W", ("sensor",), (int, float)),
    AssignmentRule(("energy",), "energy", "total_increasing", "kWh", ("sensor",), (int, float)),
    AssignmentRule(("pressure",), "pressure", "measurement", "hPa", ("sensor",), (int, float)),
    AssignmentRule(("illuminance", "brightness"), "illuminance", "measurement", "lx", ("sensor",), (int, float)),
    AssignmentRule(("co2", "pm", "tvoc"), None, "measurement", "ppm", ("sensor",), (int, float)),
    AssignmentRule(("motorposition", "motorrange"), None, "measurement", "%", ("sensor",), (int, float)),
    AssignmentRule(("alarm",), None, None, None, ("sensor",), (int, float), True),
    AssignmentRule(("mod", "devicetype", "statetext"), None, None, None, ("sensor",), (int, float, str), True),
    AssignmentRule(("deviceonline",), "connectivity", None, None, ("binary_sensor",), (bool,)),
    AssignmentRule(("openwindow",), "window", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("window",), "window", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("opendoor", "door"), "door", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("contact",), "opening", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("opened",), "opening", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("motion", "pir"), "motion", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("lowbat", "battery_low"), "battery", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("tamper",), "tamper", None, None, ("binary_sensor",), (bool, int, float, str)),
    AssignmentRule(("alarm", "error", "failed", "broken"), "problem", None, None, ("binary_sensor",), (bool, int, float, str)),
)


def assign_value(
    platform: str,
    device: LoRaWANDevice | None,
    value: LoRaWANValue | None,
) -> EntityAssignment:
    """Return Home Assistant metadata for one entity value."""
    if value is None:
        return EntityAssignment()
    if value.key.startswith("raw_") or value.key.startswith("remaining_"):
        return EntityAssignment()

    haystack = _assignment_haystack(device, value)
    for rule in DEFAULT_ASSIGNMENT_RULES:
        if rule.matches(platform, haystack, value.value):
            if rule.stop_fallback:
                return EntityAssignment()
            return EntityAssignment(
                device_class=rule.device_class,
                state_class=rule.state_class,
                unit=rule.unit,
            )

    if platform == "sensor" and isinstance(value.value, (int, float)):
        return EntityAssignment(state_class="measurement")
    return EntityAssignment()


def _assignment_haystack(
    device: LoRaWANDevice | None,
    value: LoRaWANValue,
) -> str:
    parts = [
        value.key,
        value.raw_key,
        value.name,
    ]
    if device is not None:
        parts.extend(
            [
                device.device_type or "",
                device.device_id,
                device.device_name,
                device.application_id,
                device.application_name,
            ]
        )
    return " ".join(parts).replace("_", "").replace(".", "").replace(" ", "").lower()
