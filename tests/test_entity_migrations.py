"""Tests for persisted LoRaWAN entity migrations."""

from dataclasses import dataclass, field
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "lorawan"
SPEC = importlib.util.spec_from_file_location(
    "_lorawan_entity_migrations", ROOT / "entity_migrations.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
migrate_last_open_duration_units = MODULE.migrate_last_open_duration_units


@dataclass
class Entry:
    entity_id: str
    unique_id: str
    platform: str = "lorawan"
    config_entry_id: str = "entry"
    unit_of_measurement: str | None = "s"
    options: dict = field(default_factory=dict)


class Registry:
    def __init__(self, *entries):
        self.entities = {entry.entity_id: entry for entry in entries}

    def async_update_entity(self, entity_id, **changes):
        entry = self.entities[entity_id]
        for key, value in changes.items():
            setattr(entry, key, value)

    def async_update_entity_options(self, entity_id, domain, options):
        entry = self.entities[entity_id]
        updated = dict(entry.options)
        if options is None:
            updated.pop(domain, None)
        else:
            updated[domain] = options
        entry.options = updated


class EntityMigrationTests(unittest.TestCase):
    def test_migrates_automatic_seconds_override(self):
        entry = Entry(
            "sensor.lastopenduration",
            "entry_AABB_lastopenduration",
            options={"sensor.private": {"suggested_unit_of_measurement": "s"}},
        )
        registry = Registry(entry)

        self.assertEqual(migrate_last_open_duration_units(registry, "entry"), 1)
        self.assertEqual(entry.unit_of_measurement, "min")
        self.assertNotIn("sensor.private", entry.options)

    def test_preserves_explicit_sensor_override(self):
        entry = Entry(
            "sensor.lastopenduration",
            "entry_AABB_lastopenduration",
            options={"sensor": {"unit_of_measurement": "s"}},
        )
        registry = Registry(entry)

        self.assertEqual(migrate_last_open_duration_units(registry, "entry"), 0)
        self.assertEqual(entry.unit_of_measurement, "s")

    def test_preserves_other_private_options(self):
        entry = Entry(
            "sensor.lastopenduration",
            "entry_AABB_lastopenduration",
            options={
                "sensor.private": {
                    "suggested_unit_of_measurement": "s",
                    "other": True,
                }
            },
        )
        registry = Registry(entry)

        migrate_last_open_duration_units(registry, "entry")

        self.assertEqual(entry.options["sensor.private"], {"other": True})

    def test_does_not_touch_other_entries(self):
        duration = Entry("sensor.duration", "entry_AABB_duration")
        foreign = Entry(
            "sensor.lastopenduration",
            "other_AABB_lastopenduration",
            config_entry_id="other",
        )
        registry = Registry(duration, foreign)

        self.assertEqual(migrate_last_open_duration_units(registry, "entry"), 0)
        self.assertEqual(duration.unit_of_measurement, "s")
        self.assertEqual(foreign.unit_of_measurement, "s")


if __name__ == "__main__":
    unittest.main()
