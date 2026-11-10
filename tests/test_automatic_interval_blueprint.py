"""Validate the time-based automatic interval blueprint."""
import ast
from datetime import datetime
from pathlib import Path
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
        self.inputs = {
            key: value.get("default", [])
            for key, value in self.blueprint["blueprint"]["input"].items()
        }
        self.now = datetime(2026, 7, 1)
        self.entities_by_device = {
            "device-a": ["number.device_a_interval"],
            "device-b": ["number.device_b_interval"],
            "device-c": ["number.device_c_target"],
        }
        self.devices = {
            "number.device_a_interval": {"lorawan_control_key": "intervall"},
            "number.device_b_interval": {"lorawan_control_key": "intervall"},
            "number.device_c_target": {"lorawan_control_key": "target_temperature"},
        }
        self.values = {
            "number.device_a_interval": "20",
            "number.device_b_interval": "30",
            "number.device_c_target": "21",
        }
        self.env = NativeEnvironment(undefined=StrictUndefined)
        self.env.globals.update(
            now=lambda: self.now,
            device_entities=lambda device: self.entities_by_device.get(device, []),
            state_attr=lambda entity, attribute: self.devices.get(entity, {}).get(attribute),
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

    def variables_after(self, action_index, context=None):
        context = {} if context is None else context
        context.update(self.render(self.blueprint["variables"], context))
        for action in self.blueprint["actions"][: action_index + 1]:
            if "variables" in action:
                for key, value in action["variables"].items():
                    context[key] = self.render(value, context)
        return context

    def test_inputs_and_time_trigger(self):
        meta = self.blueprint["blueprint"]
        self.assertEqual(len(meta["input"]), 76)
        self.assertEqual(
            self.blueprint["triggers"],
            [{"trigger": "time", "at": {"input": "evaluation_time"}}],
        )
        self.assertEqual(
            meta["input"]["evaluation_time"]["default"], "00:05:00"
        )
        for period in range(1, 6):
            self.assertIn(f"period_{period}_enabled", meta["input"])
            for assignment in range(1, 6):
                devices = meta["input"][
                    f"period_{period}_assignment_{assignment}_devices"
                ]
                selector = devices["selector"]["device"]
                self.assertTrue(selector["multiple"])
                self.assertEqual(selector["filter"], [{"integration": "lorawan"}])
                self.assertEqual(
                    selector["entity"],
                    [{"integration": "lorawan", "domain": "number"}],
                )

    def test_active_period_keeps_different_assignments(self):
        self.inputs.update(
            {
                "period_1_enabled": True,
                "period_1_start_month": 6,
                "period_1_start_day": 1,
                "period_1_end_month": 8,
                "period_1_end_day": 31,
                "period_1_assignment_1_devices": ["device-a", "device-b"],
                "period_1_assignment_1_interval": 30,
                "period_1_assignment_2_devices": ["device-c"],
                "period_1_assignment_2_interval": 20,
            }
        )
        context = self.variables_after(1)
        self.assertEqual(len(context["active_periods"]), 1)
        period = context["active_periods"][0]
        self.assertEqual(period["assignments"][0]["devices"], ["device-a", "device-b"])
        self.assertEqual(period["assignments"][0]["interval"], 30)
        self.assertEqual(period["assignments"][1]["devices"], ["device-c"])
        self.assertEqual(period["assignments"][1]["interval"], 20)

    def test_period_can_cross_the_end_of_the_year(self):
        self.inputs.update(
            {
                "period_1_enabled": True,
                "period_1_start_month": 10,
                "period_1_start_day": 1,
                "period_1_end_month": 3,
                "period_1_end_day": 31,
            }
        )
        self.now = datetime(2026, 1, 15)
        self.assertEqual(len(self.variables_after(1)["active_periods"]), 1)
        self.now = datetime(2026, 4, 1)
        self.assertEqual(len(self.variables_after(1)["active_periods"]), 0)

    def test_duplicate_devices_are_detected(self):
        self.inputs.update(
            {
                "period_1_enabled": True,
                "period_1_start_month": 1,
                "period_1_start_day": 1,
                "period_1_end_month": 12,
                "period_1_end_day": 31,
                "period_1_assignment_1_devices": ["device-a"],
                "period_1_assignment_2_devices": ["device-a"],
            }
        )
        context = self.variables_after(6)
        self.assertEqual(context["duplicate_devices"], ["device-a"])

    def test_resolution_targets_only_changed_interval_controls(self):
        self.inputs.update(
            {
                "period_1_enabled": True,
                "period_1_start_month": 1,
                "period_1_start_day": 1,
                "period_1_end_month": 12,
                "period_1_end_day": 31,
                "period_1_assignment_1_devices": [
                    "device-a",
                    "device-b",
                    "device-c",
                ],
                "period_1_assignment_1_interval": 30,
            }
        )
        context = self.variables_after(3)
        context["assignment_devices"] = ["device-a", "device-b", "device-c"]
        context["assignment_interval"] = 30
        repeat_action = next(
            action
            for action in self.blueprint["actions"]
            if "repeat" in action
        )
        resolution_template = repeat_action["repeat"]["sequence"][0]["then"][1][
            "variables"
        ]["resolution"]
        resolution = self.render(resolution_template, context)
        self.assertEqual(resolution["targets"], ["number.device_a_interval"])
        self.assertEqual(resolution["skipped"], ["device-c"])


if __name__ == "__main__":
    unittest.main()
