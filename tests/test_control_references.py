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
        self.runtime = Obj(entry=Obj(entry_id="lns"), downlink_controls={})
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


if __name__ == "__main__":
    unittest.main()
