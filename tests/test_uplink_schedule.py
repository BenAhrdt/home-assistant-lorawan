"""Uplink timing and HA bridge regression tests without a running HA server."""
import asyncio
import ast
from datetime import UTC, datetime, timedelta
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "lorawan"
PACKAGE = "_lorawan_schedule_tests"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package


def load(name):
    spec = importlib.util.spec_from_file_location(f"{PACKAGE}.{name}", ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


engine = load("uplink_schedule")
load("const")
START = datetime(2026, 11, 6, tzinfo=UTC)


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.state = engine.UplinkSchedule()
        self.config = {**engine.DEFAULTS, "mode": "automatic"}

    def observe(self, seconds):
        return self.state.observe(START + timedelta(seconds=seconds), self.config)

    def test_automatic_uses_accepted_anchors(self):
        self.assertIsNone(self.observe(0)["scheduled_for"])
        self.assertIsNone(self.observe(3))
        self.assertIsNone(self.observe(8))
        plan = self.observe(600)
        self.assertEqual(plan["interval_seconds"], 600)
        self.assertEqual(plan["scheduled_for"], START + timedelta(seconds=1180))
        self.assertIsNone(self.observe(603))
        self.assertEqual(self.observe(1200)["interval_seconds"], 600)

    def test_fixed_starts_on_first_uplink_and_filters_followups(self):
        self.config.update(mode="after_uplink", delay_seconds=10)
        self.assertEqual(self.observe(0)["scheduled_for"], START + timedelta(seconds=10))
        self.assertIsNone(self.observe(2))
        self.assertEqual(self.observe(600)["scheduled_for"], START + timedelta(seconds=610))

    def test_boundary_and_nonmonotonic_observations(self):
        self.observe(0)
        self.assertIsNone(self.observe(-1))
        self.assertEqual(self.observe(30)["interval_seconds"], 30)

    def test_lead_not_smaller_than_interval_does_not_fire_late(self):
        self.config["lead_seconds"] = 600
        self.observe(0)
        self.assertIsNone(self.observe(600)["scheduled_for"])

    def test_disabled_and_independent_devices(self):
        self.assertIsNone(self.state.observe(START, engine.DEFAULTS))
        other = engine.UplinkSchedule()
        self.observe(0)
        self.assertIsNone(other.anchor)
        self.assertIsNone(other.observe(START, self.config)["scheduled_for"])


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.callbacks = []
        self.events = []
        self.registry_entries = []
        self.saved = None
        self.device = types.SimpleNamespace(id="device-id", name_by_user="User name", name="Name", area_id="room")
        self.area = types.SimpleNamespace(name="Living room")
        self.hass = types.SimpleNamespace(bus=types.SimpleNamespace(async_fire=lambda *args: self.events.append(args)))
        self.runtime = types.SimpleNamespace(hass=self.hass, entry=types.SimpleNamespace(entry_id="lns"),
                                             devices={"AABB": types.SimpleNamespace(device_name="Radio name")},
                                             downlink_controls={})
        outer = self
        class Store:
            def __init__(self, *args):
                pass
            async def async_load(self):
                return outer.saved
            async def async_save(self, data):
                outer.saved = data
        def track(hass, fn, when):
            timer = {"fn": fn, "when": when, "cancelled": False}
            self.callbacks.append(timer)
            def cancel():
                timer["cancelled"] = True
            return cancel
        def module(name, **attrs):
            result = types.ModuleType(name)
            result.__dict__.update(attrs)
            return result
        device_registry = types.SimpleNamespace(async_get_device=lambda **kw: self.device)
        area_registry = types.SimpleNamespace(async_get_area=lambda area_id: self.area)
        modules = {
            "homeassistant": module("homeassistant"),
            "homeassistant.core": module("core", callback=lambda fn: fn),
            "homeassistant.helpers": module("helpers", device_registry=types.SimpleNamespace(async_get=lambda h: device_registry), area_registry=types.SimpleNamespace(async_get=lambda h: area_registry),
                entity_registry=types.SimpleNamespace(async_get=lambda h: None, async_entries_for_device=lambda registry, device_id: self.registry_entries)),
            "homeassistant.helpers.dispatcher": module("dispatcher", async_dispatcher_send=lambda *args: None),
            "homeassistant.helpers.event": module("event", async_track_point_in_utc_time=track),
            "homeassistant.helpers.storage": module("storage", Store=Store),
        }
        with patch.dict(sys.modules, modules):
            self.bridge = load("uplink_scheduler")
        self.scheduler = self.bridge.UplinkScheduler(self.runtime)
        self.scheduler.settings["AABB"] = {**engine.DEFAULTS, "mode": "after_uplink"}

    def test_one_shot_payload_uses_current_name_and_area(self):
        self.scheduler.observe("AABB")
        self.scheduler.observe("AABB")
        self.assertEqual(len(self.callbacks), 1)
        self.device.name_by_user = "Renamed Vicki"
        self.area.name = "New room name"
        self.callbacks[0]["fn"](START)
        self.assertNotIn("AABB", self.scheduler.timers)
        event, data = self.events[0]
        self.assertEqual(event, "lorawan_uplink_schedule")
        self.assertEqual(data["device_name"], "Renamed Vicki")
        self.assertEqual(data["area_name"], "New room name")
        self.assertEqual(data["device_id"], "device-id")
        self.assertEqual(data["config_entry_id"], "lns")
        self.assertEqual(data["dev_eui"], "AABB")
        self.assertIsNone(data["expected_next_uplink"])
        self.assertIsInstance(data["scheduled_for"], str)
        self.assertEqual(len(self.callbacks), 1)

    def test_event_resolves_controls_at_fire_time(self):
        unique_id = "lns_AABB_downlink_number_externaltemperature"
        self.runtime.downlink_controls[unique_id] = {
            "device": types.SimpleNamespace(dev_eui="AABB"),
            "parameter": {"name": "ExternalTemperature"},
        }
        entity = types.SimpleNamespace(
            unique_id=unique_id, entity_id="number.original", platform="lorawan",
            config_entry_id="lns", device_id="device-id", disabled_by=None,
        )
        self.registry_entries.append(entity)
        self.scheduler.observe("AABB")
        entity.entity_id = "number.renamed_after_scheduling"
        self.callbacks[0]["fn"](START)
        self.assertEqual(self.events[0][1]["controls"], {
            "external_temperature": "number.renamed_after_scheduling"})

    def test_no_room(self):
        self.device.area_id = None
        self.scheduler.observe("AABB")
        self.callbacks[0]["fn"](START)
        self.assertIsNone(self.events[0][1]["area_id"])
        self.assertIsNone(self.events[0][1]["area_name"])

    def test_reconfigure_cancels_and_persists_without_restoring_anchor(self):
        self.scheduler.observe("AABB")
        asyncio.run(self.scheduler.async_configure("AABB", "mode", "automatic"))
        self.assertTrue(self.callbacks[0]["cancelled"])
        self.assertNotIn("AABB", self.scheduler.plans)
        restored = self.bridge.UplinkScheduler(self.runtime)
        asyncio.run(restored.async_load())
        self.assertEqual(restored.config("AABB")["mode"], "automatic")
        self.assertEqual(restored.states, {})
        self.assertEqual(restored.timers, {})

    def test_next_accepted_uplink_replaces_timer_and_stop_cancels(self):
        self.scheduler.observe("AABB")
        self.scheduler.states["AABB"].anchor -= timedelta(seconds=600)
        self.scheduler.observe("AABB")
        self.assertTrue(self.callbacks[0]["cancelled"])
        self.assertFalse(self.callbacks[1]["cancelled"])
        self.scheduler.stop()
        self.assertTrue(self.callbacks[1]["cancelled"])
        self.assertEqual(self.scheduler.timers, {})

    def test_invalid_settings(self):
        for key, value in [("mode", "bad"), ("delay_seconds", 0), ("minimum_seconds", float("nan")), ("other", 20)]:
            with self.assertRaises(ValueError):
                asyncio.run(self.scheduler.async_configure("AABB", key, value))


    def test_disabled_creates_no_anchor_or_timer(self):
        self.scheduler.settings.clear()
        self.scheduler.observe("AABB")
        self.assertEqual(self.scheduler.states, {})
        self.assertEqual(self.callbacks, [])

    def test_removed_device_does_not_fire(self):
        self.scheduler.observe("AABB")
        self.runtime.devices.clear()
        self.callbacks[0]["fn"](START)
        self.assertEqual(self.events, [])
        self.assertEqual(self.scheduler.timers, {})


class DeviceTriggerTests(unittest.TestCase):
    def test_device_trigger_filters_event_and_preserves_event_backend(self):
        tree = ast.parse((ROOT / "device_trigger.py").read_text())
        method = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)
                      and node.name == "async_attach_trigger")
        calls = []
        async def attach(*args, **kwargs):
            calls.append((args, kwargs))
            return "unsubscribe"
        namespace = {"event": types.SimpleNamespace(TRIGGER_SCHEMA=lambda value: value,
                                                    async_attach_trigger=attach),
                     "CONF_PLATFORM": "platform", "CONF_DEVICE_ID": "device_id",
                     "EVENT": "lorawan_uplink_schedule"}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),
                     "device_trigger", "exec"), namespace)
        result = asyncio.run(namespace["async_attach_trigger"](
            "hass", {"device_id": "chosen-device"}, "action", "info"))
        self.assertEqual(result, "unsubscribe")
        config = calls[0][0][1]
        self.assertEqual(config["event_type"], "lorawan_uplink_schedule")
        self.assertEqual(config["event_data"], {"device_id": "chosen-device"})
        self.assertEqual(calls[0][1], {"platform_type": "device"})


if __name__ == "__main__":
    unittest.main()
