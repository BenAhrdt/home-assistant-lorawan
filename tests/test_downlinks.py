"""Regression coverage for downlink profile and CustomSend serialization."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "lorawan"
SPEC = importlib.util.spec_from_file_location("_lorawan_downlinks", ROOT / "downlinks.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CustomSendTests(unittest.TestCase):
    PROFILE = {
        "deviceType": "Vicki",
        "sendWithUplink": "enabled & collect",
        "port": 1,
        "confirmed": False,
        "priority": "NORMAL",
    }

    def test_payload_uses_profile_defaults_and_collect_mode(self):
        payload, profile, push = MODULE.custom_send_request("40", self.PROFILE)

        self.assertEqual(payload, "40")
        self.assertFalse(push)
        self.assertEqual(profile["port"], 1)
        self.assertFalse(profile["confirmed"])
        self.assertEqual(profile["priority"], "NORMAL")
        self.assertEqual(profile["sendWithUplink"], "enabled & collect")

    def test_overrides_and_push_are_parsed_in_any_order(self):
        payload, profile, push = MODULE.custom_send_request(
            "HIGH, 40, 10, true, push",
            self.PROFILE,
        )

        self.assertEqual(payload, "40")
        self.assertTrue(push)
        self.assertEqual(profile["port"], 10)
        self.assertTrue(profile["confirmed"])
        self.assertEqual(profile["priority"], "HIGH")

    def test_push_is_case_insensitive_and_does_not_change_profile_mode(self):
        payload, profile, push = MODULE.custom_send_request("40,PuSh", self.PROFILE)

        self.assertEqual(payload, "40")
        self.assertTrue(push)
        self.assertEqual(profile["sendWithUplink"], "enabled & collect")

    def test_missing_or_invalid_payload_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Hex-Payload"):
            MODULE.custom_send_request("push", self.PROFILE)
        with self.assertRaises(ValueError):
            MODULE.custom_send_request("4", self.PROFILE)
        with self.assertRaises(ValueError):
            MODULE.custom_send_request("40,AB", self.PROFILE)


if __name__ == "__main__":
    unittest.main()
