"""Regression coverage for trigger control references and registry renames."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace as Obj
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "lorawan"
spec = importlib.util.spec_from_file_location("_control_references", ROOT / "control_references.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ControlReferencesTests(unittest.TestCase):
    def setUp(self):
        self.runtime = Obj(entry=Obj(entry_id="lns"), downlink_controls={}, values={})
        self.entries = []

    def add(self, name="ExternalTemperature", suffix="downlink_number_externaltemperature", **overrides):
        unique_id = f"lns_AABB_{suffix}"
        entity = Obj(entity_id="number.external_temperature", unique_id=unique_id,
                     device_id="device", config_entry_id="lns", platform="lorawan", disabled_by=None)
        entity.__dict__.update(overrides)
        self.entries.append(entity)
        if name is not None:
            self.runtime.downlink_controls[unique_id] = {
                "device": Obj(dev_eui="AABB"), "parameter": {"name": name}}
        return entity

    def refs(self):
        return module.control_references(self.runtime, "AABB", "device", self.entries)

    def add_readable(
        self,
        key,
        domain="sensor",
        suffix=None,
        entity_category=None,
        value_key=None,
        **overrides,
    ):
        unique_id = f"lns_AABB_{suffix or key}"
        entity = Obj(
            entity_id=f"{domain}.{key}",
            unique_id=unique_id,
            device_id="device",
            config_entry_id="lns",
            platform="lorawan",
            disabled_by=None,
            entity_category=entity_category,
        )
        entity.__dict__.update(overrides)
        self.entries.append(entity)
        if not (suffix or key).startswith("uplink_schedule_"):
            self.runtime.values[unique_id] = Obj(key=value_key or key)
        return entity

    def test_technical_key_and_current_renamed_entity_id(self):
        entity = self.add()
        self.assertEqual(self.refs(), {"external_temperature": "number.external_temperature"})
        entity.entity_id = "number.renamed_by_user"
        self.assertEqual(self.refs(), {"external_temperature": "number.renamed_by_user"})

    def test_explicit_key_survives_profile_name_changes(self):
        entity = self.add(name="Different profile title")
        self.runtime.downlink_controls[entity.unique_id]["parameter"]["automation_key"] = "external_temperature"
        self.assertIn("external_temperature", self.refs())

    def test_other_devices_entries_disabled_and_foreign_platform_excluded(self):
        for overrides in ({"device_id": "other"}, {"config_entry_id": "other"},
                          {"disabled_by": "user"}, {"platform": "other"},
                          {"unique_id": "other_AABB_downlink_number_externaltemperature"}):
            with self.subTest(overrides=overrides):
                self.entries.clear()
                self.add(**overrides)
                self.assertEqual(self.refs(), {})

    def test_stale_downlink_and_sensors_excluded(self):
        self.add(name=None)
        self.add(name=None, suffix="temperature", entity_id="sensor.temperature")
        self.assertEqual(self.refs(), {})

    def test_composed_and_config_controls_have_stable_scoped_keys(self):
        self.add(name=None, suffix="climate_1234", entity_id="climate.my_room")
        self.add(name=None, suffix="uplink_schedule_mode", entity_id="select.mode")
        self.assertEqual(self.refs(), {"climate_1234": "climate.my_room",
                                      "select_uplink_schedule_mode": "select.mode"})

    def test_collisions_are_omitted_instead_of_selecting_arbitrary_target(self):
        self.add()
        self.add(name="external_temperature", suffix="downlink_number_other", entity_id="number.other")
        self.assertEqual(self.refs(), {})

    def test_all_downlink_platforms(self):
        for domain in ("number", "select", "switch", "button", "text"):
            self.add(name=f"Test{domain.title()}", suffix=f"downlink_{domain}_test",
                     entity_id=f"{domain}.test")
        self.assertEqual(len(self.refs()), 5)

    def test_motor_calibration_button_has_blueprint_contract_key(self):
        self.add(name="MotorCalibration", suffix="downlink_button_motorcalibration",
                 entity_id="button.motor_calibration")
        self.assertEqual(self.refs(), {
            "motor_calibration": "button.motor_calibration",
        })

    def test_entity_references_group_active_current_entities(self):
        self.add(name=None, suffix="next_send_push", entity_id="button.next_send_push")
        self.add_readable("room_temperature")
        self.add_readable("online", domain="binary_sensor")
        self.add_readable(
            "next_send",
            suffix="downlink_next_send",
            entity_id="sensor.next_send_hex",
            entity_category="diagnostic",
            value_key="downlink_next_send",
        )
        self.add_readable(
            "expected",
            suffix="uplink_schedule_expected_next_uplink",
            entity_id="sensor.expected_next_uplink",
            entity_category="diagnostic",
        )

        references = module.entity_references(self.runtime, "AABB", "device", self.entries)

        self.assertEqual(references["controls"], {
            "button_next_send_push": "button.next_send_push",
        })
        self.assertEqual(references["sensors"], {
            "room_temperature": "sensor.room_temperature",
        })
        self.assertEqual(references["binary_sensors"], {
            "online": "binary_sensor.online",
        })
        self.assertEqual(references["diagnostics"], {
            "expected_next_uplink": "sensor.expected_next_uplink",
            "next_send_hex": "sensor.next_send_hex",
        })

    def test_entity_references_omit_disabled_stale_and_ambiguous_entities(self):
        self.add_readable("stale", suffix="stale", entity_id="sensor.stale")
        del self.runtime.values["lns_AABB_stale"]
        self.add_readable("disabled", entity_id="sensor.disabled", disabled_by="user")
        self.add_readable("duplicate", entity_id="sensor.first", value_key="same")
        self.add_readable("other", entity_id="sensor.second", value_key="same")

        references = module.entity_references(self.runtime, "AABB", "device", self.entries)

        self.assertEqual(references["sensors"], {})


if __name__ == "__main__":
    unittest.main()
