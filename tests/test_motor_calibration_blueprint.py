"""Execute the time-based motor-calibration blueprint with simulated HA helpers."""
import ast
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace as Obj
import unittest

try:
    import yaml
    from jinja2 import StrictUndefined
    from jinja2.nativetypes import NativeEnvironment
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipIf(yaml is None, "Requires PyYAML and Jinja2")
class MotorCalibrationBlueprintTests(unittest.TestCase):
    def setUp(self):
        class Loader(yaml.SafeLoader):
            pass

        Loader.add_constructor(
            "!input", lambda loader, node: {"input": loader.construct_scalar(node)}
        )
        path = ROOT / "blueprints/automation/lorawan/weekly_motor_calibration.yaml"
        self.blueprint = yaml.load(path.read_text(), Loader=Loader)
        self.now = datetime(2026, 11, 8, 12, 0, tzinfo=UTC)  # Sunday
        self.inputs = {
            "calibration_devices": ["vicki-one", "vicki-two"],
            "calibration_weekday": "sun",
            "calibration_time": "12:00:00",
            "calibration_cycle": "before",
        }
        self.entities_by_device = {
            "vicki-one": ["button.vicki_one_motor", "button.vicki_one_infos"],
            "vicki-two": ["button.vicki_two_motor"],
        }
        self.devices = {
            "button.vicki_one_motor": "vicki-one",
            "button.vicki_one_infos": "vicki-one",
            "button.vicki_two_motor": "vicki-two",
        }
        self.attributes = {
            "button.vicki_one_motor": {"lorawan_control_key": "motor_calibration"},
            "button.vicki_one_infos": {"lorawan_control_key": "get_infos"},
            "button.vicki_two_motor": {"lorawan_control_key": "motor_calibration"},
        }
        self.env = NativeEnvironment(undefined=StrictUndefined)
        self.env.globals.update(
            now=lambda: self.now,
            device_entities=lambda device: self.entities_by_device.get(device, []),
            device_id=lambda entity: self.devices.get(entity),
            state_attr=lambda entity, attr: self.attributes.get(entity, {}).get(attr),
        )

    def render(self, value, context):
        if isinstance(value, dict):
            if set(value) == {"input"}:
                return self.inputs[value["input"]]
            return {key: self.render(item, context) for key, item in value.items()}
        if isinstance(value, str):
            result = self.env.from_string(value).render(**context)
            if isinstance(result, str) and ("{{" in value or "{%" in value):
                result = result.strip()
                try:
                    return ast.literal_eval(result)
                except (ValueError, SyntaxError):
                    pass
            return result
        return value

    def run_blueprint(self, manual=False):
        context = {} if manual else {"trigger": Obj(platform="time")}
        context.update(self.render(self.blueprint["variables"], context))
        for action in self.blueprint["actions"]:
            if "variables" in action:
                for key, value in action["variables"].items():
                    context[key] = self.render(value, context)
            elif "if" in action:
                if all(
                    self.render(condition["value_template"], context)
                    for condition in action["if"]
                ):
                    return {"stop": self.render(action["then"][0]["stop"], context)}
            elif "action" in action:
                return self.render(action, context)
        self.fail("No result")

    def test_input_selector_and_time_trigger(self):
        meta = self.blueprint["blueprint"]
        self.assertEqual(set(meta["input"]), set(self.inputs))
        selector = meta["input"]["calibration_devices"]["selector"]["device"]
        self.assertTrue(selector["multiple"])
        self.assertEqual(
            selector["filter"],
            [{"integration": "lorawan", "model": "Vicki"}],
        )
        self.assertEqual(self.blueprint["triggers"][0]["trigger"], "time")
        self.assertEqual(self.blueprint["triggers"][0]["at"], {"input": "calibration_time"})

    def test_selected_devices_press_only_motor_calibration_buttons(self):
        result = self.run_blueprint()
        self.assertEqual(result["action"], "button.press")
        self.assertEqual(
            result["target"],
            {"entity_id": ["button.vicki_one_motor", "button.vicki_two_motor"]},
        )
        self.inputs["calibration_cycle"] = "after"
        self.assertEqual(self.run_blueprint()["target"], result["target"])

    def test_weekday_and_manual_runs_stop(self):
        self.now = datetime(2026, 11, 9, 12, 0, tzinfo=UTC)  # Monday
        self.assertIn("Wochentag", self.run_blueprint()["stop"])
        self.assertIn("Zeittrigger", self.run_blueprint(manual=True)["stop"])

    def test_missing_or_ambiguous_motor_control_stops(self):
        self.entities_by_device["vicki-two"] = []
        self.assertIn("MotorCalibration", self.run_blueprint()["stop"])
        self.entities_by_device["vicki-two"] = [
            "button.vicki_two_motor",
            "button.vicki_two_motor_duplicate",
        ]
        self.devices["button.vicki_two_motor_duplicate"] = "vicki-two"
        self.attributes["button.vicki_two_motor_duplicate"] = {
            "lorawan_control_key": "motor_calibration"
        }
        self.assertIn("MotorCalibration", self.run_blueprint()["stop"])

    def test_renamed_entity_is_resolved_by_stable_control_key(self):
        self.entities_by_device["vicki-one"] = ["button.renamed_motor"]
        self.devices["button.renamed_motor"] = "vicki-one"
        self.attributes["button.renamed_motor"] = {
            "lorawan_control_key": "motor_calibration"
        }
        result = self.run_blueprint()
        self.assertIn("button.renamed_motor", result["target"]["entity_id"])


if __name__ == "__main__":
    unittest.main()
