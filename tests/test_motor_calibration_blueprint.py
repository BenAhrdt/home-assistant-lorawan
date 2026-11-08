"""Execute the motor-calibration blueprint templates with simulated HA helpers.

PyYAML/Jinja2 are test-only dependencies; this is not full HA schema validation.
"""
import ast
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace as Obj
import math
import unittest
from zoneinfo import ZoneInfo

try:
    import yaml
    from jinja2 import StrictUndefined
    from jinja2.nativetypes import NativeEnvironment
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ZoneInfo("Europe/Berlin")


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
        self.now = datetime(2026, 11, 8, 10, 54, 40, tzinfo=UTC)
        self.inputs = {
            "calibration_devices": ["vicki"],
            "calibration_weekday": "sun",
            "calibration_time": "12:00:00",
            "calibration_cycle": "before",
        }
        self.values = {"button.motor_calibration": "unknown"}
        self.devices = {"button.motor_calibration": "vicki"}
        self.data = {
            "source": "lorawan",
            "mode": "automatic",
            "device_id": "vicki",
            "interval_seconds": 600,
            "last_uplink": "2026-11-08T10:45:00+00:00",
            "expected_next_uplink": "2026-11-08T10:55:00+00:00",
            "controls": {"motor_calibration": "button.motor_calibration"},
        }
        self.env = NativeEnvironment(undefined=StrictUndefined)

        def states(entity):
            return self.values.get(entity, "unknown")

        def numeric(value):
            try:
                return math.isfinite(float(value))
            except (ValueError, TypeError):
                return False

        def as_datetime(value):
            if isinstance(value, datetime):
                return value
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value, UTC)
            return datetime.fromisoformat(value.replace("Z", "+00:00"))

        def as_timestamp(value, default=None):
            try:
                return as_datetime(value).timestamp()
            except (AttributeError, TypeError, ValueError):
                return default

        def today_at(value):
            parsed = time.fromisoformat(str(value))
            local_now = self.now.astimezone(LOCAL)
            return datetime.combine(local_now.date(), parsed, LOCAL)

        self.env.globals.update(
            states=states,
            device_id=lambda entity: self.devices.get(entity),
            is_number=numeric,
            as_datetime=as_datetime,
            as_timestamp=as_timestamp,
            as_local=lambda value: value.astimezone(LOCAL),
            now=lambda: self.now.astimezone(LOCAL),
            today_at=today_at,
            timedelta=timedelta,
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

    def test_inputs_source_and_device_filter(self):
        meta = self.blueprint["blueprint"]
        self.assertEqual(set(meta["input"]), set(self.inputs))
        selector = meta["input"]["calibration_devices"]["selector"]["device"]
        self.assertTrue(selector["multiple"])
        self.assertEqual(
            selector["filter"], [{"integration": "lorawan", "model": "Vicki"}]
        )
        self.assertTrue(
            meta["source_url"].endswith(
                "/main/blueprints/automation/lorawan/weekly_motor_calibration.yaml"
            )
        )
        self.assertEqual(
            self.blueprint["triggers"][0]["event_data"], {"source": "lorawan"}
        )

    def test_last_cycle_before_time_presses_event_button(self):
        result = self.run_blueprint()
        self.assertEqual(result["action"], "button.press")
        self.assertEqual(
            result["target"], {"entity_id": "button.motor_calibration"}
        )

    def test_first_cycle_after_time(self):
        self.inputs["calibration_cycle"] = "after"
        self.data["last_uplink"] = "2026-11-08T10:55:00+00:00"
        self.data["expected_next_uplink"] = "2026-11-08T11:05:00+00:00"
        self.now = datetime(2026, 11, 8, 11, 4, 40, tzinfo=UTC)
        self.assertEqual(self.run_blueprint()["action"], "button.press")

    def test_other_cycles_do_not_press(self):
        self.data["last_uplink"] = "2026-11-08T10:55:00+00:00"
        self.data["expected_next_uplink"] = "2026-11-08T11:05:00+00:00"
        self.now = datetime(2026, 11, 8, 11, 4, 40, tzinfo=UTC)
        self.assertIn("Uplink-Zyklus", self.run_blueprint()["stop"])
        self.inputs["calibration_cycle"] = "after"
        self.data["last_uplink"] = "2026-11-08T10:45:00+00:00"
        self.data["expected_next_uplink"] = "2026-11-08T10:55:00+00:00"
        self.now = datetime(2026, 11, 8, 10, 54, 40, tzinfo=UTC)
        self.assertIn("Uplink-Zyklus", self.run_blueprint()["stop"])

    def test_exact_time_is_valid_for_both_preferences(self):
        self.data["last_uplink"] = "2026-11-08T10:50:00+00:00"
        self.data["expected_next_uplink"] = "2026-11-08T11:00:00+00:00"
        self.now = datetime(2026, 11, 8, 10, 59, 40, tzinfo=UTC)
        self.assertEqual(self.run_blueprint()["action"], "button.press")
        self.inputs["calibration_cycle"] = "after"
        self.assertEqual(self.run_blueprint()["action"], "button.press")

    def test_week_boundary_uses_next_monday_for_before(self):
        self.inputs["calibration_weekday"] = "mon"
        self.inputs["calibration_time"] = "00:00:00"
        self.data["last_uplink"] = "2026-11-08T22:45:00+00:00"
        self.data["expected_next_uplink"] = "2026-11-08T22:55:00+00:00"
        self.now = datetime(2026, 11, 8, 22, 54, 40, tzinfo=UTC)
        self.assertEqual(self.run_blueprint()["action"], "button.press")

    def test_requires_real_automatic_selected_device(self):
        self.assertIn("Kein Ereignis", self.run_blueprint(manual=True)["stop"])
        for mode in ("after_uplink", "disabled"):
            with self.subTest(mode=mode):
                self.data["mode"] = mode
                self.assertIn("automatic", self.run_blueprint()["stop"])
        self.data["mode"] = "automatic"
        self.inputs["calibration_devices"] = ["other"]
        self.assertIn("nicht", self.run_blueprint()["stop"])

    def test_missing_wrong_or_unavailable_control_stops(self):
        self.data["controls"] = {}
        self.assertIn("MotorCalibration", self.run_blueprint()["stop"])
        self.data["controls"] = {
            "motor_calibration": "number.motor_calibration"
        }
        self.assertIn("MotorCalibration", self.run_blueprint()["stop"])
        self.data["controls"] = {
            "motor_calibration": "button.motor_calibration"
        }
        self.devices["button.motor_calibration"] = "other"
        self.assertIn("MotorCalibration", self.run_blueprint()["stop"])
        self.devices["button.motor_calibration"] = "vicki"
        self.values["button.motor_calibration"] = "unavailable"
        self.assertIn("MotorCalibration", self.run_blueprint()["stop"])

    def test_incomplete_prediction_stops(self):
        for key, value in (
            ("expected_next_uplink", None),
            ("last_uplink", None),
            ("interval_seconds", None),
            ("interval_seconds", 0),
        ):
            with self.subTest(key=key, value=value):
                original = self.data[key]
                self.data[key] = value
                self.assertIn("Vorhersage", self.run_blueprint()["stop"])
                self.data[key] = original

    def test_button_timestamp_prevents_duplicate_weekly_occurrence(self):
        self.values["button.motor_calibration"] = "2026-11-08T10:54:00+00:00"
        self.assertIn("bereits", self.run_blueprint()["stop"])
        self.values["button.motor_calibration"] = "2026-11-01T10:54:00+00:00"
        self.assertEqual(self.run_blueprint()["action"], "button.press")
