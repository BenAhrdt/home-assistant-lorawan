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
        self.rule = {
            "name": "Target temperature",
            "enabled": True,
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
        return str(value).strip().lower() not in {
            "nan",
            "inf",
            "infinity",
            "-inf",
            "-infinity",
        }

    def render(self, template, context):
        result = self.env.from_string(template).render(**context)
        if isinstance(result, str):
            result = result.strip()
            try:
                return ast.literal_eval(result)
            except (ValueError, SyntaxError):
                return result
        return result

    def evaluation_template(self):
        def find(node):
            if isinstance(node, list):
                for item in node:
                    found = find(item)
                    if found is not None:
                        return found
            elif isinstance(node, dict):
                variables = node.get("variables")
                if isinstance(variables, dict) and "evaluation" in variables:
                    return variables["evaluation"]
                for value in node.values():
                    found = find(value)
                    if found is not None:
                        return found
            return None

        template = find(self.blueprint["actions"])
        self.assertIsNotNone(template)
        return template

    def evaluate(self, *, rule=None, rule_state=None, entity=None, event_entities=None):
        active_rule = rule or self.rule
        context = {
            "rules": [active_rule],
            "rule_states": [rule_state or {"count": 0, "retries": 0}],
            "wait": Obj(
                trigger=Obj(
                    event=Obj(
                        data={
                            "entity_ids": event_entities
                            if event_entities is not None
                            else [entity or active_rule["uplink_entity"]]
                        }
                    )
                )
            ),
        }
        return self.render(self.evaluation_template(), context)

    def test_repeatable_rule_input_and_entity_event_trigger(self):
        metadata = self.blueprint["blueprint"]
        self.assertEqual(set(metadata["input"]), {"rules"})
        rules_input = metadata["input"]["rules"]
        selector = rules_input["selector"]["object"]
        self.assertTrue(selector["multiple"])
        self.assertEqual(selector["label_field"], "name")
        self.assertEqual(selector["description_field"], "enabled")
        self.assertTrue(selector["fields"]["enabled"]["default"])
        self.assertEqual(selector["fields"]["uplinks_to_check"]["default"], 2)
        self.assertEqual(
            set(selector["fields"]),
            {
                "name",
                "enabled",
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
        self.assertEqual(self.blueprint["triggers"][0], {
            "trigger": "homeassistant",
            "event": "start",
        })
        self.assertEqual(self.blueprint["triggers"][1], {
            "trigger": "time_pattern",
            "minutes": "/1",
        })
        wait = self.blueprint["actions"][2]["repeat"]["sequence"][0]["wait_for_trigger"]
        self.assertEqual(wait, [{"trigger": "event", "event_type": "lorawan_entities_updated"}])

    def test_uplink_updates_are_counted_before_comparison(self):
        rule = {**self.rule, "uplinks_to_check": 2}
        first = self.evaluate(rule=rule, entity=rule["uplink_entity"])
        self.assertEqual(first["states"], [{"count": 1, "retries": 0}])
        self.assertEqual(first["actions"], [])

        second = self.evaluate(
            rule=rule,
            rule_state=first["states"][0],
            entity=rule["uplink_entity"],
        )
        self.assertEqual(second["states"], [{"count": 0, "retries": 0}])
        self.assertEqual(second["actions"], [])

    def test_only_the_selected_uplink_entity_is_counted(self):
        result = self.evaluate(event_entities=["sensor.other_entity"])
        self.assertEqual(result, {"states": [{"count": 0, "retries": 0}], "actions": []})

    def test_disabled_rule_is_not_counted_or_retried(self):
        result = self.evaluate(
            rule={**self.rule, "enabled": False},
            event_entities=[self.rule["uplink_entity"]],
        )
        self.assertEqual(result, {"states": [{"count": 0, "retries": 0}], "actions": []})

    def test_unchanged_sensor_state_is_still_counted_by_uplink_event(self):
        result = self.evaluate(
            rule={**self.rule, "uplinks_to_check": 2},
            event_entities=[self.rule["uplink_entity"]],
        )
        self.assertEqual(result["states"], [{"count": 1, "retries": 0}])

    def test_failed_comparison_rewrites_the_current_number_value(self):
        self.values["sensor.target_temperature"] = "20.0"
        result = self.evaluate()
        self.assertEqual(result["states"], [{"count": 0, "retries": 1}])
        self.assertEqual(
            result["actions"],
            [{
                "downlink_entity": "number.target_temperature",
                "downlink_domain": "number",
                "current_downlink_value": "21",
            }],
        )

    def test_all_existing_comparison_rules_remain_available(self):
        options = self.blueprint["blueprint"]["input"]["rules"]["selector"]["object"]["fields"][
            "comparison_rule"
        ]["selector"]["select"]["options"]
        values = {option["value"] for option in options}
        self.assertEqual(len(values), 12)
        self.assertIn("uplink_equal_downlink", values)
        self.assertIn("uplink_greater_or_equal_value", values)

        self.values["sensor.target_temperature"] = "22"
        self.assertEqual(
            self.evaluate(
                rule={**self.rule, "comparison_rule": "uplink_greater_or_equal_value", "comparison_value": "22"}
            )["actions"],
            [],
        )
        self.values["sensor.target_temperature"] = "20"
        self.assertEqual(
            self.evaluate(
                rule={**self.rule, "comparison_rule": "uplink_less_downlink"}
            )["actions"],
            [],
        )

    def test_downlink_filter_prevents_counting_when_it_does_not_match(self):
        rule = {**self.rule, "downlink_filter_operator": "equal", "downlink_filter_value": "20"}
        result = self.evaluate(rule=rule)
        self.assertEqual(result, {"states": [{"count": 0, "retries": 0}], "actions": []})

    def test_retry_actions_cover_supported_domains(self):
        actions = self.blueprint["actions"][2]["repeat"]["sequence"][3]["repeat"]["sequence"][0]["choose"]
        self.assertEqual(
            {
                item["sequence"][0]["action"]
                for item in actions
            },
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
