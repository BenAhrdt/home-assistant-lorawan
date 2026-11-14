"""Migrate persisted Home Assistant entity options for LoRaWAN values."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any


def migrate_last_open_duration_units(
    registry: Any,
    config_entry_id: str,
    domain: str = "lorawan",
) -> int:
    """Replace the old automatic seconds display with the native minutes unit.

    Home Assistant preserves a previously used unit in the entity registry when
    an integration changes its native unit. Only the private suggestion created
    by that compatibility migration is removed; an explicit user unit override
    remains untouched.
    """
    private_domain = "sensor.private"
    migrated = 0
    for entry in registry.entities.values():
        if (
            entry.platform != domain
            or entry.config_entry_id != config_entry_id
            or not str(entry.entity_id).startswith("sensor.")
            or not str(entry.unique_id).endswith(
                ("_lastopenduration", "_last_open_duration")
            )
            or entry.unit_of_measurement != "s"
        ):
            continue

        options: MutableMapping[str, Any] = dict(entry.options or {})
        sensor_options = options.get("sensor") or {}
        if "unit_of_measurement" in sensor_options:
            continue

        registry.async_update_entity(
            entry.entity_id,
            unit_of_measurement="min",
        )

        private_options = dict(options.get(private_domain) or {})
        if private_options.get("suggested_unit_of_measurement") == "s":
            del private_options["suggested_unit_of_measurement"]
            registry.async_update_entity_options(
                entry.entity_id,
                private_domain,
                private_options or None,
            )
        migrated += 1
    return migrated
