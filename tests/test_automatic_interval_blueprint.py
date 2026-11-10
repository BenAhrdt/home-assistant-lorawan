"""Validate the repeatable time/assignment interval blueprint."""
import ast
from datetime import datetime
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
class AutomaticIntervalBlueprintTests(unittest.TestCase):
    def setUp(self):
        class Loader(yaml.SafeLoader):
            pass

        Loader.add_constructor(
            "!input", lambda loader, node: {"input": loader.construct_scalar(node)}
        )
        path = ROOT / "blueprints/automation/lorawan/automatic_interval.yaml"
        self.blueprint = yaml.load(path.read_text(), Loader=Loader)
        self.schedule = [
            {
                "name": "Sommer",
                "month": 6,
                "day": 1,
                "time": "12:30:00",
                "assignments": [
                    {"name": "Langsam", "devices": ["device-a"], "interval": 30},
                    {"name": "Schnell", "devices": ["device-b"], "interval": 20},
                ],
            }
        ]
        self.inputs = {"schedule": self.schedule}
        self.now = datetime(2026, 6, 1, 12, 30)
        self.entities_by_device = {
            "device-a": ["number.device_a_interval"],
            "device-b": ["number.device_b_interval"],
            "device-c": ["number.device_c_target"],
        }
        self.attributes = {
            "number.device_a_interval": {
                "lorawan_control_key": "intervall",
                "min": 5,
                "max": 60,
            },
            "number.device_b_interval": {
                "lorawan_control_key": "intervall",
                "min": 5,
                "max": 60,
            },
            "number.device_c_target": {
                "lorawan_control_key": "target_temperature",
                "min": 6,
                "max": 30,
            },
        }
        self.values = {
            "number.device_a_interval": "20",
            "number.device_b_interval": "20",
            "number.device_c_target": "21",
        }
        self.env = NativeEnvironment(undefined=StrictUndefined)
        self.env.globals.update(
            now=lambda: self.now,
            device_entities=lambda device: self.entities_by_device.get(device, []),
            device_attr=lambda device, attribute: (
                "Thermostat A" if device == "device-a" and attribute == "name" else None
            ),
            state_attr=lambda entity, attribute: self.attributes.get(entity, {}).get(attribute),
            states=lambda entity: self.values.get(entity, "unknown"),
        )

    def render(self, value, context):
        if isinstance(value, dict):
            if set(value) == {"input"}:
                return self.inputs[value["input"]]
            return {key: self.render(item, context) for key, item in value.items()}
        if isinstance(value, list):
            return [self.render(item, context) for item in value]
        if isinstance(value, str) and ("{{" in value or "{%" in value):
            result = self.env.from_string(value).render(**context)
            if isinstance(result, str):
                result = result.strip()
                try:
                    return ast.literal_eval(result)
                except (ValueError, SyntaxError):
                    pass
            return result
        return value

    def variables_after(self, action_index):
        context = {}
        context.update(self.render(self.blueprint["variables"], context))
        for action in self.blueprint["actions"][: action_index + 1]:
            if "variables" in action:
                for key, value in action["variables"].items():
                    context[key] = self.render(value, context)
        return context

    def test_repeatable_nested_selector_and_time_trigger(self):
        meta = self.blueprint["blueprint"]
        self.assertEqual(set(meta["input"]), {"schedule"})
        schedule_selector = meta["input"]["schedule"]["selector"]["object"]
        self.assertTrue(schedule_selector["multiple"])
        self.assertNotIn("description", schedule_selector["fields"]["time"])
        self.assertIn("month", schedule_selector["fields"])
        self.assertIn("day", schedule_selector["fields"])
        self.assertNotIn("date", schedule_selector["fields"])
        month_options = schedule_selector["fields"]["month"]["selector"]["select"][
            "options"
        ]
        self.assertEqual([option["value"] for option in month_options], [str(i) for i in range(1, 13)])
        self.assertEqual(
            self.blueprint["triggers"],
            [{"trigger": "time_pattern", "minutes": "/1"}],
        )
        assignment_selector = schedule_selector["fields"]["assignments"]["selector"]["object"]
        self.assertTrue(assignment_selector["multiple"])
        device_selector = assignment_selector["fields"]["devices"]["selector"]["device"]
        self.assertTrue(device_selector["multiple"])

    def test_month_day_schedule_and_assignments_are_flattened(self):
        context = self.variables_after(3)
        self.assertEqual(len(context["active_schedule"]), 1)
        self.assertEqual(len(context["active_assignments"]), 2)
        self.assertEqual(context["active_assignments"][0]["interval"], 30)
        self.assertEqual(context["active_assignments"][1]["interval"], 20)

    def test_optional_time_defaults_to_ten_am(self):
        self.schedule[0].pop("time")
        self.now = datetime(2026, 6, 1, 10, 0)
        self.assertEqual(len(self.variables_after(1)["active_schedule"]), 1)

    def test_non_matching_time_is_not_active(self):
        self.now = datetime(2026, 6, 1, 12, 31)
        self.assertEqual(len(self.variables_after(1)["active_schedule"]), 0)

    def test_duplicate_devices_are_detected(self):
        self.schedule[0]["assignments"][1]["devices"] = ["device-a"]
        context = self.variables_after(5)
        self.assertEqual(context["duplicate_devices"], ["device-a"])

    def test_resolution_targets_changed_interval_control_only(self):
        self.schedule[0]["assignments"].append(
            {"name": "Nicht Intervall", "devices": ["device-c"], "interval": 30}
        )
        context = self.variables_after(3)
        context["assignment_devices"] = ["device-a", "device-c"]
        context["assignment_interval"] = 30
        repeat_action = next(action for action in self.blueprint["actions"] if "repeat" in action)
        resolution_template = repeat_action["repeat"]["sequence"][0]["then"][1][
            "variables"
        ]["resolution"]
        resolution = self.render(resolution_template, context)
        self.assertEqual(resolution["targets"], ["number.device_a_interval"])
        self.assertEqual(resolution["skipped"], ["device-c"])

    def test_single_device_without_name_uses_device_name_fallback(self):
        repeat_action = next(action for action in self.blueprint["actions"] if "repeat" in action)
        assignment_template = repeat_action["repeat"]["sequence"][0]["then"][0][
            "variables"
        ]["assignment_name"]
        result = self.render(
            assignment_template,
            {"repeat": Obj(item={"devices": ["device-a"], "interval": 30})},
        )
        self.assertEqual(result, "Thermostat A")


if __name__ == "__main__":
    unittest.main()
