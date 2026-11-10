"""Execute the delayed Next Send Push blueprint with simulated HA helpers."""
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
class NextSendPushBlueprintTests(unittest.TestCase):
    def setUp(self):
        class Loader(yaml.SafeLoader):
            pass

        Loader.add_constructor(
            "!input", lambda loader, node: {"input": loader.construct_scalar(node)}
        )
        path = ROOT / "blueprints/automation/lorawan/next_send_push.yaml"
        self.blueprint = yaml.load(path.read_text(), Loader=Loader)
        self.inputs = {"target_devices": [], "push_delay_seconds": 5}
        self.data = {
            "source": "lorawan",
            "mode": "automatic",
            "device_id": "vicki",
            "entities": {
                "controls": {"button_next_send_push": "button.next_send_push"},
                "diagnostics": {"next_send_hex": "sensor.next_send_hex"},
            },
        }
        self.values = {"sensor.next_send_hex": "3C00BA"}
        self.devices = {
            "button.next_send_push": "vicki",
            "sensor.next_send_hex": "vicki",
        }
        self.env = NativeEnvironment(undefined=StrictUndefined)

        def states(entity):
            return self.values.get(entity, "unknown")

        self.env.globals.update(
            states=states,
            device_id=lambda entity: self.devices.get(entity),
            has_value=lambda entity: states(entity) not in ("unknown", "unavailable"),
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
        context = {} if manual else {"trigger": Obj(event=Obj(data=self.data))}
        context.update(self.render(self.blueprint["variables"], context))
        delay = None
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
            elif "delay" in action:
                delay = self.render(action["delay"], context)
            elif "action" in action:
                result = self.render(action, context)
                if delay is not None:
                    result["_delay"] = delay
                return result
        self.fail("No result")

    def test_input_selector_and_trigger(self):
        meta = self.blueprint["blueprint"]
        self.assertEqual(set(meta["input"]), set(self.inputs))
        selector = meta["input"]["target_devices"]["selector"]["device"]
        self.assertTrue(selector["multiple"])
        self.assertEqual(selector["filter"], [{"integration": "lorawan"}])
        self.assertEqual(meta["input"]["target_devices"]["default"], [])
        self.assertEqual(meta["input"]["push_delay_seconds"]["default"], 5)
        self.assertEqual(
            self.blueprint["triggers"][0]["event_data"], {"source": "lorawan"}
        )

    def test_waits_then_pushes_current_queued_downlink(self):
        result = self.run_blueprint()
        self.assertEqual(result["_delay"], {"seconds": 5})
        self.assertEqual(result["action"], "button.press")
        self.assertEqual(result["target"], {"entity_id": "button.next_send_push"})

    def test_empty_queue_is_not_pushed(self):
        for state in ("0", "unknown", "unavailable"):
            with self.subTest(state=state):
                self.values["sensor.next_send_hex"] = state
                self.assertIn("kein Downlink", self.run_blueprint()["stop"])
        self.values["sensor.next_send_hex"] = "3C00BA"

    def test_device_selection_is_optional_or_restrictive(self):
        self.assertEqual(self.run_blueprint()["action"], "button.press")
        self.inputs["target_devices"] = ["other"]
        self.assertIn("nicht ausgewählt", self.run_blueprint()["stop"])
        self.inputs["target_devices"] = ["vicki"]
        self.assertEqual(self.run_blueprint()["action"], "button.press")

    def test_wrong_mode_or_references_stop(self):
        self.data["mode"] = "disabled"
        self.assertIn("aktiver", self.run_blueprint()["stop"])
        self.data["mode"] = "automatic"
        self.data["entities"]["diagnostics"] = {}
        self.assertIn("Referenzen", self.run_blueprint()["stop"])
        self.data["entities"]["diagnostics"]["next_send_hex"] = "sensor.next_send_hex"
        self.devices["sensor.next_send_hex"] = "other"
        self.assertIn("Referenzen", self.run_blueprint()["stop"])

    def test_manual_run_stops(self):
        self.assertIn("aktiver", self.run_blueprint(manual=True)["stop"])


if __name__ == "__main__":
    unittest.main()
