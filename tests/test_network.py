"""Network regression checks without requiring a Home Assistant installation."""
import ast
import asyncio
from collections import deque
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "lorawan"
PACKAGE = "_lorawan_network_tests"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package


def load(name):
    spec = importlib.util.spec_from_file_location(f"{PACKAGE}.{name}", ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


load("models")
normalizer = load("normalizer")
uplinks = load("uplinks")


def ttn(metadata=None):
    return normalizer.normalize_message("v3/test@ttn/devices/sensor/up", {
        "end_device_ids": {"device_id": "sensor", "dev_eui": "AABB", "application_ids": {"application_id": "test"}},
        "uplink_message": {"rx_metadata": metadata or [], "decoded_payload": {"temperature": 21}, "f_cnt": 0, "f_port": 1,
                           "settings": {"frequency": "868100000", "data_rate": {"lora": {"spreading_factor": 7}}}},
    })


class NetworkTests(unittest.TestCase):
    def test_ttn_keeps_all_gateways_and_zero_values(self):
        message = ttn([{"gateway_ids": {"gateway_id": "one"}, "rssi": 0, "channel_rssi": -90, "snr": 0},
                       {"gateway_ids": {"gateway_id": "two"}, "rssi": -110, "snr": -5}])
        self.assertEqual([g["gateway_id"] for g in message.attributes["gateways"]], ["one", "two"])
        self.assertEqual(message.attributes["rssi"], 0)
        self.assertEqual(message.attributes["gateways"][0]["snr"], 0)
        self.assertEqual(message.attributes["spreading_factor"], 7)

    def test_chirpstack_keeps_all_gateways(self):
        message = normalizer.normalize_message("application/app/device/AABB/event/up", {
            "deviceInfo": {"devEui": "AABB", "applicationId": "app"},
            "rxInfo": [{"gatewayId": "one", "rssi": -80, "snr": 0}, {"gatewayId": "two", "rssi": -100, "snr": -7}],
            "txInfo": {"frequency": 868100000, "modulation": {"lora": {"spreadingFactor": 9}}},
        })
        self.assertEqual(len(message.attributes["gateways"]), 2)
        self.assertEqual(message.attributes["gateways"][1]["snr"], -7)
        self.assertEqual(message.attributes["spreading_factor"], 9)

    def test_missing_and_partial_metadata(self):
        self.assertEqual(ttn().attributes["gateways"], [])
        message = ttn([None, {}, {"gateway_ids": {"eui": "0011"}, "channel_rssi": -92}])
        self.assertEqual(message.attributes["gateways"][-1], {"gateway_id": "0011", "rssi": -92})

    def test_history_bounded_newest_first_and_independent(self):
        history = {}
        message = ttn([{"gateway_ids": {"gateway_id": "one"}, "snr": 0}])
        for counter in range(25):
            message.attributes["f_cnt"] = counter
            uplinks.remember_uplink(history, message, f"time-{counter}")
        records = history["AABB"]
        self.assertEqual(len(records), 20)
        self.assertEqual([r["f_cnt"] for r in records], list(range(24, 4, -1)))
        message.attributes["gateways"][0]["gateway_id"] = "changed"
        self.assertEqual(records[0]["gateways"][0]["gateway_id"], "one")
        self.assertEqual(records[0]["decoded"], {"temperature": 21})
        self.assertEqual(records[0]["received_at"], "time-24")

    def test_join_does_not_replace_uplink(self):
        history = {}
        message = ttn()
        uplinks.remember_uplink(history, message, "first")
        for event in ("join", "joined", "ack", "status", "down"):
            message.message_type = event
            uplinks.remember_uplink(history, message, "later")
        self.assertEqual(len(history["AABB"]), 1)
        self.assertEqual(history["AABB"][0]["received_at"], "first")

    def test_lns_histories_are_independent(self):
        first, second = {}, {}
        uplinks.remember_uplink(first, ttn(), "first")
        uplinks.remember_uplink(second, ttn(), "second")
        self.assertEqual(first["AABB"][0]["received_at"], "first")
        self.assertEqual(second["AABB"][0]["received_at"], "second")

    def test_cache_roundtrip_and_legacy_cache(self):
        tree = ast.parse((ROOT / "runtime.py").read_text())
        runtime_class = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LoRaWANRuntime")
        methods = [n for n in runtime_class.body if isinstance(n, ast.AsyncFunctionDef) and n.name in {"async_load_cache", "async_save_cache"}]
        namespace = {"deque": deque, "UPLINK_HISTORY_LIMIT": 20}
        exec(compile(ast.fix_missing_locations(ast.Module(body=methods, type_ignores=[])), "cache", "exec"), namespace)
        class Store:
            data = {"uplinks_by_device": {"AABB": [{"f_cnt": i} for i in range(25)]}}
            async def async_load(self):
                return deepcopy(self.data)
            async def async_save(self, data):
                self.data = deepcopy(data)
        store = Store()
        runtime = types.SimpleNamespace(_store=store)
        asyncio.run(namespace["async_load_cache"](runtime))
        self.assertEqual(len(runtime.uplinks_by_device["AABB"]), 20)
        asyncio.run(namespace["async_save_cache"](runtime))
        restored = types.SimpleNamespace(_store=store)
        asyncio.run(namespace["async_load_cache"](restored))
        self.assertEqual(restored.uplinks_by_device, runtime.uplinks_by_device)
        store.data = {"devices": {}}
        asyncio.run(namespace["async_load_cache"](restored))
        self.assertEqual(restored.uplinks_by_device, {})

    def test_history_endpoint_scopes_lns_and_handles_missing_entry(self):
        tree = ast.parse((ROOT / "__init__.py").read_text())
        function = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "_websocket_device_uplinks")
        function.decorator_list = []
        namespace = {"DOMAIN": "lorawan", "_clean_dev_eui": str.upper}
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), function], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "endpoint", "exec"), namespace)
        hass = types.SimpleNamespace(data={"lorawan": {
            "lns-one": types.SimpleNamespace(uplinks_by_device={"AABB": [{"f_cnt": 1}]}),
            "lns-two": types.SimpleNamespace(uplinks_by_device={"AABB": [{"f_cnt": 2}]}),
        }})
        results = []
        connection = types.SimpleNamespace(send_result=lambda _, value: results.append(value))
        for entry in ("lns-two", "missing"):
            asyncio.run(namespace["_websocket_device_uplinks"](hass, connection, {"id": 1, "entry_id": entry, "dev_eui": "aabb"}))
        self.assertEqual(results, [{"uplinks": [{"f_cnt": 2}]}, {"uplinks": []}])


if __name__ == "__main__":
    unittest.main()
