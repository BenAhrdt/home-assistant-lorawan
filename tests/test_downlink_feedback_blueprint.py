"""Validate the generic downlink feedback/retry blueprint."""
import ast
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
class DownlinkFeedbackBlueprintTests(unittest.TestCase):
    def setUp(self):
        class Loader(yaml.SafeLoader):
            pass

        Loader.add_constructor(
            "!input", lambda loader, node: {"input": loader.construct_scalar(node)}
        )
        path = ROOT / "blueprints/automation/lorawan/downlink_feedback_retry_entities_v3.yaml"
        self.blueprint = yaml.load(path.read_text(), Loader=Loader)
        self.inputs = {
            "downlink_entity": "number.target_temperature",
            "uplink_entity": "sensor.target_temperature",
            "downlink_filter_operator": "all",
            "downlink_filter_value": "",
            "comparison_rule": "uplink_equal_downlink",
            "comparison_value": "",
            "uplinks_to_check": 1,
            "max_retries": 3,
        }
        self.values = {
            "number.target_temperature": "21",
            "sensor.target_temperature": "21.0",
        }
        self.devices = {
            "number.target_temperature": "vicki",
            "sensor.target_temperature": "vicki",
        }
        self.env = NativeEnvironment(undefined=StrictUndefined)
        self.env.globals.update(
            states=lambda entity: self.values.get(entity, "unknown"),
            device_id=lambda entity: self.devices.get(entity),
            has_value=lambda entity: self.values.get(entity, "unknown")
            not in {"unknown", "unavailable"},
            is_number=lambda value: self._is_number(value),
        )

    @staticmethod
    def _is_number(value):
        try:
            float(value)
        except (TypeError, ValueError):
            return False
        return str(value).strip().lower() not in {"nan", "inf", "infinity", "-inf", "-infinity"}

    def render(self, template, context):
        result = self.env.from_string(template).render(**context)
        if isinstance(result, str):
            result = result.strip()
            try:
                return ast.literal_eval(result)
            except (ValueError, SyntaxError):
                return result
        return result

    def filter_template(self):
        return self.blueprint["actions"][1]["variables"]["downlink_filter_matches"]

    def comparison_template(self):
        action = next(
            action
            for action in self.blueprint["actions"]
            if "variables" in action and "comparison_matches" in action["variables"]
        )
        return action["variables"]["comparison_matches"]

    def context(self):
        context = dict(self.inputs)
        context.update(
            downlink_entity=self.inputs["downlink_entity"],
            uplink_entity=self.inputs["uplink_entity"],
            downlink_filter_operator=self.inputs["downlink_filter_operator"],
            downlink_filter_value=self.inputs["downlink_filter_value"],
            comparison_rule=self.inputs["comparison_rule"],
            comparison_value=self.inputs["comparison_value"],
        )
        context["downlink_filter_matches"] = self.render(self.filter_template(), context)
        return context

    def test_inputs_and_filters(self):
        metadata = self.blueprint["blueprint"]
        self.assertEqual(
            set(metadata["input"]),
            {
                "downlink_entity",
                "uplink_entity",
                "downlink_filter_operator",
                "downlink_filter_value",
                "comparison_rule",
                "comparison_value",
                "uplinks_to_check",
                "max_retries",
            },
        )
        self.assertEqual(self.blueprint["mode"], "single")
        self.assertEqual(self.blueprint["triggers"][0]["trigger"], "homeassistant")
        self.assertEqual(self.blueprint["triggers"][0]["event"], "start")
        self.assertEqual(self.blueprint["triggers"][1], {
            "trigger": "time_pattern",
            "minutes": "/1",
        })
        self.assertEqual(
            self.blueprint["actions"][5]["repeat"]["count"],
            "{{ max_retries | int(1) }}",
        )
        derived_device = self.blueprint["actions"][0]["variables"]
        self.assertEqual(
            derived_device["downlink_device"],
            "{{ device_id(downlink_entity) or '' }}",
        )
        scope_check = next(
            action for action in self.blueprint["actions"]
            if action.get("alias") == "Entitäten und gemeinsames Gerät prüfen"
        )
        self.assertIn("device_id(uplink_entity) != downlink_device", scope_check["if"][0]["condition"]["value_template"])
        self.assertNotIn("equality_tolerance", metadata["input"])
        self.assertEqual(
            metadata["input"]["downlink_filter_value"]["visible"],
            {"field": "downlink_filter_operator", "operator": "not_eq", "value": "all"},
        )
        self.assertEqual(
            metadata["input"]["comparison_value"]["visible"]["operator"], "in"
        )
        filter_options = metadata["input"]["downlink_filter_operator"]["selector"]["select"]["options"]
        self.assertEqual(filter_options[0]["value"], "all")
        self.assertIn("greater_or_equal", [option["value"] for option in filter_options])

    def test_downlink_filter_is_type_aware(self):
        context = self.context()
        self.assertTrue(self.render(self.filter_template(), context))

        self.inputs.update(downlink_filter_operator="equal", downlink_filter_value="21")
        self.assertTrue(self.render(self.filter_template(), self.context()))

        self.inputs.update(downlink_filter_operator="greater", downlink_filter_value="22")
        self.assertFalse(self.render(self.filter_template(), self.context()))

        self.values["number.target_temperature"] = "heat"
        self.inputs.update(downlink_filter_operator="equal", downlink_filter_value="heat")
        self.assertTrue(self.render(self.filter_template(), self.context()))

    def test_feedback_compares_current_downlink_or_fixed_value(self):
        self.inputs["comparison_rule"] = "uplink_equal_downlink"
        self.assertTrue(self.render(self.comparison_template(), self.context()))

        self.values["number.target_temperature"] = "20"
        self.assertFalse(self.render(self.comparison_template(), self.context()))

        self.inputs.update(
            comparison_rule="uplink_greater_or_equal_value", comparison_value="20"
        )
        self.assertTrue(self.render(self.comparison_template(), self.context()))

    def test_retry_actions_cover_supported_domains(self):
        choose = next(action for action in self.blueprint["actions"] if "choose" in action)
        actions = [
            item["sequence"][0]["action"]
            for item in choose["choose"]
            if item["sequence"] and "action" in item["sequence"][0]
        ]
        self.assertEqual(
            set(actions),
            {
                "number.set_value",
                "select.select_option",
                "switch.turn_on",
                "switch.turn_off",
                "text.set_value",
            },
        )


if __name__ == "__main__":
    unittest.main()
