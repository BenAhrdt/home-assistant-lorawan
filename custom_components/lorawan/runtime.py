"""Runtime MQTT handling for LoRaWAN."""

from __future__ import annotations

import json
import base64
import logging
import re
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.storage import Store
from paho.mqtt import client as mqtt_client

from .assigner import assign_value
from .const import (
    CONF_CREATE_RAW_SENSORS,
    CONF_CREATE_REMAINING_SENSORS,
    CONF_DEVICE_CREATE_RAW_SENSORS,
    CONF_DEVICE_CREATE_REMAINING_SENSORS,
    CONF_DEVICE_OFFLINE_AFTER_HOURS,
    CONF_DOWNLINK_PROFILES,
    CONF_OFFLINE_AFTER_HOURS,
    CONF_SSL,
    DEFAULT_MQTT_PORT,
    DEFAULT_OFFLINE_AFTER_HOURS,
    DEFAULT_TOPIC_FILTERS,
    SIGNAL_ADD_BINARY_SENSOR,
    SIGNAL_ADD_DOWNLINK_CONTROL,
    SIGNAL_REMOVE_DOWNLINK_CONTROL,
    SIGNAL_ADD_SENSOR,
    SIGNAL_DEVICE_ADDED,
    SIGNAL_UPDATE_DOWNLINK_CONTROLS,
    SIGNAL_UPDATE_ENTITY,
)
from .models import LoRaWANDevice, LoRaWANMessage, LoRaWANValue
from .normalizer import normalize_message
from .downlinks import (
    INTERNAL_BASE_PROFILE,
    downlink_message,
    merged_profiles,
    parameter_payload,
    profile_for_device,
    state_options,
)

_LOGGER = logging.getLogger(__name__)

UnsubscribeCallback = Callable[[], None]
STORAGE_VERSION = 1
STORAGE_KEY_PREFIX = "lorawan_runtime"


class LoRaWANRuntime:
    """Manage MQTT subscriptions and entity state."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        config = dict(entry.data)
        config.update(entry.options)
        self.host: str = config.get(CONF_HOST, "")
        self.port: int = config.get(CONF_PORT, DEFAULT_MQTT_PORT)
        self.use_ssl: bool = config.get(CONF_SSL, False)
        self.username: str = config.get(CONF_USERNAME, "")
        self.password: str = config.get(CONF_PASSWORD, "")
        self.topic_filters: list[str] = list(DEFAULT_TOPIC_FILTERS)
        self.create_raw_sensors: bool = config.get(CONF_CREATE_RAW_SENSORS, True)
        self.create_remaining_sensors: bool = config.get(
            CONF_CREATE_REMAINING_SENSORS,
            False,
        )
        self.offline_after_hours: int = config.get(
            CONF_OFFLINE_AFTER_HOURS,
            DEFAULT_OFFLINE_AFTER_HOURS,
        )
        self.device_offline_after_hours: dict[str, int] = {
            _clean_dev_eui(dev_eui): int(hours)
            for dev_eui, hours in (
                config.get(CONF_DEVICE_OFFLINE_AFTER_HOURS) or {}
            ).items()
        }
        self.device_create_raw_sensors: dict[str, bool] = {
            _clean_dev_eui(dev_eui): bool(enabled)
            for dev_eui, enabled in (
                config.get(CONF_DEVICE_CREATE_RAW_SENSORS) or {}
            ).items()
        }
        self.device_create_remaining_sensors: dict[str, bool] = {
            _clean_dev_eui(dev_eui): bool(enabled)
            for dev_eui, enabled in (
                config.get(CONF_DEVICE_CREATE_REMAINING_SENSORS) or {}
            ).items()
        }
        self.downlink_profiles: list[dict[str, Any]] = list(config.get(CONF_DOWNLINK_PROFILES) or [])
        self.downlink_controls: dict[str, dict[str, Any]] = {}
        self.devices: dict[str, LoRaWANDevice] = {}
        self.values: dict[str, LoRaWANValue] = {}
        self.value_devices: dict[str, LoRaWANDevice] = {}
        self.entity_platforms: dict[str, str] = {}
        self._mqtt_client: mqtt_client.Client | None = None
        self._unsub_offline_timer: UnsubscribeCallback | None = None
        self.connected = False
        self.last_error: str | None = None
        self.last_connected_at: str | None = None
        self.last_disconnected_at: str | None = None
        self.last_message_at: str | None = None
        self.last_topic: str | None = None
        self.recent_messages: deque[dict[str, str]] = deque(maxlen=10)
        self.message_count = 0
        self.unsupported_message_count = 0
        self.lns_counts = {"ttn": 0, "chirpstack": 0}
        self.downlink_event_count = 0
        self.downlink_event_counts: dict[str, int] = {}
        self.last_downlink_event_at: str | None = None
        self.last_downlink_topic: str | None = None
        self.last_seen_by_device: dict[str, str] = {}
        self.last_downlink_by_device: dict[str, dict[str, Any]] = {}
        self.next_downlink_by_device: dict[str, dict[str, Any]] = {}
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{STORAGE_KEY_PREFIX}_{entry.entry_id}",
        )

    async def async_start(self) -> None:
        """Connect to the configured MQTT broker and subscribe to uplinks."""
        await self.async_load_cache()
        self._refresh_device_online_states()
        self._unsub_offline_timer = async_track_time_interval(
            self.hass,
            self._async_check_device_online_states,
            timedelta(hours=1),
        )

        if not self.host:
            self.last_error = "MQTT broker host is not configured"
            _LOGGER.warning("LoRaWAN %s", self.last_error)
            return

        client = mqtt_client.Client(client_id=f"home-assistant-lorawan-{self.entry.entry_id}")
        client.on_connect = self._on_mqtt_connect
        client.on_disconnect = self._on_mqtt_disconnect
        client.on_message = self._on_mqtt_message

        if self.username:
            client.username_pw_set(self.username, self.password or None)
        if self.use_ssl:
            client.tls_set()

        self._mqtt_client = client
        client.connect_async(self.host, self.port, keepalive=60)
        client.loop_start()
        _LOGGER.debug("Started LoRaWAN MQTT client for %s:%s", self.host, self.port)

    async def async_stop(self) -> None:
        """Stop the MQTT client."""
        if self._unsub_offline_timer is not None:
            self._unsub_offline_timer()
            self._unsub_offline_timer = None
        await self.async_save_cache()
        if self._mqtt_client is None:
            return
        self._mqtt_client.disconnect()
        self._mqtt_client.loop_stop()
        self._mqtt_client = None

    def send_downlink(self, network: str, device: LoRaWANDevice, profile: dict[str, Any], payload_hex: str) -> None:
        """Publish one encoded downlink through the active MQTT connection."""
        if self._mqtt_client is None or not self.connected:
            raise RuntimeError("MQTT ist nicht verbunden")
        topic, payload = downlink_message(network, device, profile, payload_hex)
        result = self._mqtt_client.publish(topic, json.dumps(payload), qos=0)
        if result.rc != mqtt_client.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Downlink konnte nicht veröffentlicht werden (MQTT-Code {result.rc})")
        self._store_downlink_diagnostics(device, payload_hex, payload)
        _LOGGER.info("Published LoRaWAN downlink for %s on %s", device.dev_eui, topic)

    def _on_mqtt_connect(
        self,
        client: mqtt_client.Client,
        userdata: Any,
        flags: dict[str, Any],
        result_code: int,
    ) -> None:
        """Subscribe after MQTT has connected."""
        if result_code != 0:
            self.connected = False
            self.last_error = f"MQTT connection failed with code {result_code}"
            _LOGGER.warning("LoRaWAN MQTT connection failed with code %s", result_code)
            return

        self.connected = True
        self.last_error = None
        self.last_connected_at = _utc_now()
        for topic_filter in self.topic_filters:
            client.subscribe(topic_filter)
            _LOGGER.debug("Subscribed to LoRaWAN MQTT topic filter %s", topic_filter)

    def _on_mqtt_disconnect(
        self,
        client: mqtt_client.Client,
        userdata: Any,
        result_code: int,
    ) -> None:
        """Log MQTT disconnects."""
        self.connected = False
        self.last_disconnected_at = _utc_now()
        if result_code:
            self.last_error = f"MQTT disconnected with code {result_code}"
            _LOGGER.warning("LoRaWAN MQTT disconnected with code %s", result_code)

    def _on_mqtt_message(
        self,
        client: mqtt_client.Client,
        userdata: Any,
        msg: mqtt_client.MQTTMessage,
    ) -> None:
        """Forward one MQTT message from the Paho thread to Home Assistant."""
        try:
            payload = msg.payload.decode("utf-8")
        except UnicodeDecodeError as err:
            self.last_error = f"Non-UTF-8 payload on {msg.topic}"
            _LOGGER.warning("Ignoring non-UTF-8 LoRaWAN MQTT payload on %s: %s", msg.topic, err)
            return

        self.hass.loop.call_soon_threadsafe(
            self._async_message_received,
            msg.topic,
            payload,
        )

    @callback
    def _async_message_received(self, topic: str, raw_payload: str) -> None:
        """Handle one MQTT message."""
        try:
            payload = json.loads(raw_payload)
        except (TypeError, json.JSONDecodeError) as err:
            self.last_error = f"Invalid JSON on {topic}"
            _LOGGER.warning("Ignoring invalid LoRaWAN JSON on %s: %s", topic, err)
            return

        downlink_event = _downlink_event(topic)
        if downlink_event is not None:
            self._store_downlink_event(topic, raw_payload, downlink_event)
            return

        normalized = normalize_message(topic, payload)
        if normalized is None:
            self.unsupported_message_count += 1
            self.last_error = f"Unsupported LoRaWAN message on {topic}"
            _LOGGER.debug("Ignoring unsupported LoRaWAN message on %s", topic)
            return

        self.message_count += 1
        self.last_message_at = _utc_now()
        self.last_topic = topic
        network = normalized.attributes.get("network")
        if network in self.lns_counts:
            self.lns_counts[network] += 1
        self.last_error = None
        self.recent_messages.appendleft(
            {
                "topic": topic,
                "payload": raw_payload,
                "received_at": self.last_message_at,
            }
        )
        self._store_message(normalized)

    @callback
    def _store_downlink_event(
        self,
        topic: str,
        raw_payload: str,
        event: str,
    ) -> None:
        """Store a downlink event without treating it as an uplink."""
        received_at = _utc_now()
        self.downlink_event_count += 1
        self.downlink_event_counts[event] = self.downlink_event_counts.get(event, 0) + 1
        self.last_downlink_event_at = received_at
        self.last_downlink_topic = topic
        self.last_error = None
        self.recent_messages.appendleft(
            {
                "topic": topic,
                "payload": raw_payload,
                "received_at": received_at,
                "direction": "downlink",
                "event": event,
            }
        )
        self.hass.async_create_task(self.async_save_cache())

    @callback
    def _store_message(self, message: LoRaWANMessage) -> None:
        device = message.device
        is_new_device = device.dev_eui not in self.devices
        existing_device = self.devices.get(device.dev_eui)
        if existing_device is not None and existing_device.device_type:
            # A type already learned from an earlier uplink or entered manually
            # is authoritative. Uplinks only initialize an empty device type.
            device.device_type = existing_device.device_type
        self.devices[device.dev_eui] = device
        self._refresh_downlink_controls()
        self.last_seen_by_device[device.dev_eui] = self.last_message_at or _utc_now()
        if is_new_device:
            async_dispatcher_send(
                self.hass,
                SIGNAL_DEVICE_ADDED,
                self.entry.entry_id,
                device.dev_eui,
            )
        values = [self._device_online_value(device, True)]
        values.extend(self._downlink_diagnostic_values(device))
        values.extend(message.decoded)
        values.extend(message.raw)
        values.extend(message.remaining)

        for value in values:
            if not value.key.startswith("device_"):
                value.attributes.update(message.attributes)
            self._store_value(device, value)
        self._send_queued_downlink(device)
        self.hass.async_create_task(self.async_save_cache())

    @callback
    def _store_value(self, device: LoRaWANDevice, value: LoRaWANValue) -> None:
        """Store one value and notify Home Assistant if needed."""
        entity_id = self.entity_key(device, value)
        is_new = entity_id not in self.values
        self.values[entity_id] = value
        self.value_devices[entity_id] = device

        platform = self.platform_for_value(value)
        previous_platform = self.entity_platforms.get(entity_id)
        if is_new:
            self.entity_platforms[entity_id] = platform
            signal = SIGNAL_ADD_BINARY_SENSOR if platform == "binary_sensor" else SIGNAL_ADD_SENSOR
            async_dispatcher_send(self.hass, signal, self.entry.entry_id, entity_id)
        elif previous_platform == platform:
            async_dispatcher_send(self.hass, SIGNAL_UPDATE_ENTITY, entity_id)

    @callback
    def _async_check_device_online_states(self, now: datetime) -> None:
        """Refresh device online sensors periodically."""
        self._refresh_device_online_states()
        self.hass.async_create_task(self.async_save_cache())

    @callback
    def _refresh_device_online_states(self) -> None:
        """Update online sensors from last seen timestamps."""
        for device in self.devices.values():
            self._store_value(
                device,
                self._device_online_value(
                    device,
                    self._is_device_online(device.dev_eui),
                ),
            )
            for value in self._downlink_diagnostic_values(device):
                self._store_value(device, value)

    def _is_device_online(self, dev_eui: str) -> bool:
        """Return true if a device has reported within the configured window."""
        last_seen = _parse_utc(self.last_seen_by_device.get(dev_eui))
        if last_seen is None:
            return False
        return datetime.now(UTC) - last_seen <= timedelta(
            hours=self.offline_after_hours_for_device(dev_eui)
        )

    def is_device_online(self, dev_eui: str) -> bool:
        """Return the current online state for a device."""
        return self._is_device_online(dev_eui)

    def offline_after_hours_for_device(self, dev_eui: str) -> int:
        """Return the offline threshold for one device."""
        return self.device_offline_after_hours.get(
            _clean_dev_eui(dev_eui),
            self.offline_after_hours,
        )

    def create_raw_sensors_for_device(self, dev_eui: str) -> bool:
        """Return whether raw sensors are enabled for one device."""
        return self.device_create_raw_sensors.get(
            _clean_dev_eui(dev_eui), self.create_raw_sensors
        )

    def create_remaining_sensors_for_device(self, dev_eui: str) -> bool:
        """Return whether remaining-payload sensors are enabled for one device."""
        return self.device_create_remaining_sensors.get(
            _clean_dev_eui(dev_eui), self.create_remaining_sensors
        )

    def _device_online_value(self, device: LoRaWANDevice, online: bool) -> LoRaWANValue:
        """Return the synthetic per-device online value."""
        last_seen = self.last_seen_by_device.get(device.dev_eui)
        return LoRaWANValue(
            key="device_online",
            name="Online",
            value=online,
            raw_key="device.online",
            attributes={
                "last_seen_at": last_seen,
                "offline_after_hours": self.offline_after_hours_for_device(device.dev_eui),
            },
        )

    def _downlink_diagnostic_values(self, device: LoRaWANDevice) -> list[LoRaWANValue]:
        """Return the queued and most recently sent downlink diagnostics."""
        last = self.last_downlink_by_device.get(device.dev_eui, {})
        values = [
            LoRaWANValue(
                key="downlink_next_send",
                name="Next Send Hex",
                value=self.next_downlink_by_device.get(device.dev_eui, {}).get("hex", "0"),
                raw_key="downlink.nextSend.hex",
            ),
            LoRaWANValue(
                key="downlink_last_send_hex",
                name="Last Send Hex",
                value=last.get("hex", "0"),
                raw_key="downlink.lastSend.hex",
            ),
        ]
        payload_hex = str(last.get("hex", ""))
        payload_json = last.get("json")
        if payload_hex or payload_json:
            try:
                raw_bytes = bytes.fromhex(payload_hex)
            except ValueError:
                raw_bytes = b""
            values.extend(
                [
                    LoRaWANValue(
                        key="downlink_raw_json",
                        name="Downlink Raw JSON",
                        value=payload_json or {},
                        raw_key="downlink.raw.json",
                    ),
                    LoRaWANValue(
                        key="downlink_raw_base64",
                        name="Downlink Raw Base64",
                        value=base64.b64encode(raw_bytes).decode(),
                        raw_key="downlink.raw.base64",
                    ),
                    LoRaWANValue(
                        key="downlink_raw_hex",
                        name="Downlink Raw Hex",
                        value=payload_hex,
                        raw_key="downlink.raw.hex",
                    ),
                    LoRaWANValue(
                        key="downlink_raw_string",
                        name="Downlink Raw String",
                        value=raw_bytes.decode(errors="replace"),
                        raw_key="downlink.raw.string",
                    ),
                ]
            )
        return values

    def _store_downlink_diagnostics(
        self,
        device: LoRaWANDevice,
        payload_hex: str,
        payload_json: dict[str, Any],
    ) -> None:
        """Store and publish diagnostics after a successful downlink."""
        self.last_downlink_by_device[device.dev_eui] = {
            "hex": payload_hex,
            "json": payload_json,
        }
        for value in self._downlink_diagnostic_values(device):
            self._store_value(device, value)
        self.hass.async_create_task(self.async_save_cache())

    def _queue_downlink(
        self,
        device: LoRaWANDevice,
        profile: dict[str, Any],
        payload_hex: str,
    ) -> None:
        """Queue a downlink until the next uplink, optionally collecting payloads."""
        if profile.get("sendWithUplink") == "enabled & collect":
            payload_hex = (
                self.next_downlink_by_device.get(device.dev_eui, {}).get("hex", "")
                + payload_hex
            )
        self.next_downlink_by_device[device.dev_eui] = {
            "hex": payload_hex,
            "profile": profile,
        }
        for value in self._downlink_diagnostic_values(device):
            self._store_value(device, value)
        self.hass.async_create_task(self.async_save_cache())

    def _send_queued_downlink(self, device: LoRaWANDevice) -> None:
        """Send a device's queued payload after receiving an uplink."""
        queued = self.next_downlink_by_device.pop(device.dev_eui, None)
        if queued is None:
            return
        network = device.network or (
            "ttn" if "@" in device.application_name else "chirpstack"
        )
        try:
            self.send_downlink(network, device, queued["profile"], queued["hex"])
        except Exception as err:
            self.next_downlink_by_device[device.dev_eui] = queued
            _LOGGER.warning("Queued downlink for %s could not be sent: %s", device.dev_eui, err)
        for value in self._downlink_diagnostic_values(device):
            self._store_value(device, value)

    def push_queued_downlink(self, dev_eui: str) -> None:
        """Immediately send the payload waiting for a device's next uplink."""
        device = self.devices.get(_clean_dev_eui(dev_eui))
        if device is None:
            raise ValueError("Unbekanntes LoRaWAN-Gerät")
        if device.dev_eui not in self.next_downlink_by_device:
            raise ValueError("Kein Downlink wartet auf den Versand")
        self._send_queued_downlink(device)

    def entity_key(self, device: LoRaWANDevice, value: LoRaWANValue) -> str:
        """Return the stable internal key for a value."""
        return f"{self.entry.entry_id}_{device.dev_eui}_{value.key}"

    def platform_for_value(self, value: LoRaWANValue) -> str:
        """Choose the Home Assistant platform for a value."""
        if isinstance(value.value, bool):
            return "binary_sensor"
        assignment = assign_value("binary_sensor", None, value)
        if assignment.device_class is not None:
            return "binary_sensor"
        return "sensor"

    def entities_for_platform(self, platform: str) -> list[str]:
        """Return entity keys currently belonging to a platform."""
        return [
            entity_key
            for entity_key, entity_platform in self.entity_platforms.items()
            if entity_platform == platform
        ]

    def get_value(self, entity_key: str) -> LoRaWANValue | None:
        """Return the current value for an entity key."""
        return self.values.get(entity_key)

    def get_device(self, entity_key: str) -> LoRaWANDevice | None:
        """Return the device for an entity key."""
        return self.value_devices.get(entity_key)

    def diagnostics_for_device(self, dev_eui: str) -> dict[str, Any]:
        """Return the most recent raw and remaining MQTT data for one device."""
        device = self.devices.get(_clean_dev_eui(dev_eui))
        if device is None:
            return {"raw": None, "remaining": None}

        def value_for(key: str) -> Any:
            value = self.values.get(f"{self.entry.entry_id}_{device.dev_eui}_{key}")
            return value.value if value is not None else None

        return {
            "raw": value_for("raw_json"),
            "remaining": value_for("remaining_json"),
        }

    def _refresh_downlink_controls(self) -> None:
        """Create control descriptors for every device's matching downlink profile."""
        controls: dict[str, dict[str, Any]] = {}
        profiles = merged_profiles(self.downlink_profiles)
        for device in self.devices.values():
            profile = profile_for_device(profiles, device.device_type)
            base_profile = next(
                (
                    item
                    for item in profiles
                    if item.get("deviceType") == INTERNAL_BASE_PROFILE["deviceType"]
                ),
                INTERNAL_BASE_PROFILE,
            )
            parameters: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
            base_parameter_names = {
                str(parameter.get("name", ""))
                for parameter in base_profile.get("downlinkParameter", [])
            }
            for parameter in base_profile.get("downlinkParameter", []):
                networks = parameter.get("networks")
                if networks and device.network not in networks:
                    continue
                parameters[str(parameter.get("name", ""))] = (base_profile, parameter)
            if profile is not None and profile.get("deviceType") != INTERNAL_BASE_PROFILE["deviceType"]:
                for parameter in profile.get("downlinkParameter", []):
                    networks = parameter.get("networks")
                    if networks and device.network not in networks:
                        continue
                    parameters[str(parameter.get("name", ""))] = (profile, parameter)
            for index, (parameter_profile, parameter) in enumerate(parameters.values()):
                options = state_options(parameter)
                platform = {"number": "number", "boolean": "switch", "button": "button", "ascii": "text", "string": "text", "json": "text"}.get(parameter.get("type"))
                if parameter.get("type") == "number" and options:
                    platform = "select"
                if platform is None:
                    continue
                slug = re.sub(r"[^a-z0-9_]+", "_", str(parameter.get("name", "parameter")).casefold()).strip("_")
                scope = "base_" if str(parameter.get("name", "")) in base_parameter_names else ""
                key = f"{self.entry.entry_id}_{device.dev_eui}_downlink_{platform}_{scope}{slug or index}"
                controls[key] = {"device": device, "profile": parameter_profile, "parameter": parameter, "platform": platform, "state_options": options}
        previous_controls = self.downlink_controls
        self.downlink_controls = controls
        if previous_controls != controls:
            for key in previous_controls.keys() - controls.keys():
                async_dispatcher_send(self.hass, SIGNAL_REMOVE_DOWNLINK_CONTROL, self.entry.entry_id, key)
            registry = er.async_get(self.hass)
            prefix = f"{self.entry.entry_id}_"
            for entity in list(registry.entities.values()):
                if (
                    entity.config_entry_id == self.entry.entry_id
                    and entity.unique_id.startswith(prefix)
                    and "_downlink_" in entity.unique_id
                    and "_downlink_next_send" not in entity.unique_id
                    and "_downlink_last_send_" not in entity.unique_id
                    and entity.unique_id not in controls
                ):
                    registry.async_remove(entity.entity_id)
            async_dispatcher_send(self.hass, SIGNAL_UPDATE_DOWNLINK_CONTROLS)
        for key in controls:
            if key not in previous_controls:
                async_dispatcher_send(
                    self.hass,
                    SIGNAL_ADD_DOWNLINK_CONTROL,
                    self.entry.entry_id,
                    key,
                )

    def downlink_controls_for_platform(self, platform: str) -> list[str]:
        """Return current control keys for one Home Assistant entity platform."""
        self._refresh_downlink_controls()
        return [key for key, control in self.downlink_controls.items() if control["platform"] == platform]

    def get_downlink_control(self, entity_key: str) -> dict[str, Any] | None:
        """Return one downlink control descriptor."""
        return self.downlink_controls.get(entity_key)

    def set_device_type(self, dev_eui: str, device_type: str) -> None:
        """Set a device type and rebuild its downlink controls."""
        device = self.devices.get(_clean_dev_eui(dev_eui))
        if device is None:
            raise ValueError("Unbekanntes LoRaWAN-Gerät")
        device.device_type = device_type.strip() or None
        self._refresh_downlink_controls()
        self.hass.async_create_task(self.async_save_cache())

    def send_downlink_control(self, entity_key: str, value: Any) -> None:
        """Encode and publish a Home Assistant control value as a downlink."""
        control = self.downlink_controls.get(entity_key)
        if control is None:
            raise RuntimeError("Downlink-Steuerung ist nicht verfügbar")
        device = control["device"]
        parameter = control["parameter"]
        profile = control["profile"]
        if parameter.get("type") == "json":
            try:
                payload = json.loads(str(value))
            except json.JSONDecodeError as err:
                raise ValueError("Downlink muss gültiges JSON sein") from err
            if not isinstance(payload, dict):
                raise ValueError("Downlink-JSON muss ein Objekt sein")
            network = device.network or (
                "ttn" if "@" in device.application_name else "chirpstack"
            )
            if network == "ttn":
                application, _, tenant = device.application_name.partition("@")
                app = application or device.application_id
                mode = "replace" if parameter.get("name") == "replace" else "push"
                topic = f"v3/{app}{'@' + tenant if tenant else ''}/devices/{device.device_id}/down/{mode}"
            elif network == "chirpstack":
                topic = f"application/{device.application_id}/device/{device.dev_eui}/command/down"
            else:
                raise ValueError("Unbekannter LoRaWAN-Netzwerkserver")
            if self._mqtt_client is None or not self.connected:
                raise RuntimeError("MQTT ist nicht verbunden")
            self._mqtt_client.publish(topic, json.dumps(payload))
            payload_hex = ""
            downlinks = payload.get("downlinks")
            encoded = (
                downlinks[0].get("frm_payload")
                if isinstance(downlinks, list) and downlinks
                else payload.get("data")
            )
            if isinstance(encoded, str):
                try:
                    payload_hex = base64.b64decode(encoded).hex().upper()
                except Exception:
                    payload_hex = ""
            self._store_downlink_diagnostics(device, payload_hex, payload)
            return
        payload = parameter_payload(parameter, value)
        network = device.network or ("ttn" if "@" in device.application_name else "chirpstack")
        if profile.get("sendWithUplink", "disabled") != "disabled":
            self._queue_downlink(device, {**profile, **parameter}, payload)
            return
        self.send_downlink(network, device, {**profile, **parameter}, payload)

    async def async_load_cache(self) -> None:
        """Load cached devices and values from Home Assistant storage."""
        data = await self._store.async_load()
        if not data:
            return

        self.devices = {
            dev_eui: _device_from_json(device)
            for dev_eui, device in (data.get("devices") or {}).items()
        }
        self.last_seen_by_device = dict(data.get("last_seen_by_device") or {})
        cached_value_devices = data.get("value_devices") or {}
        self.values = {}
        for entity_key, value_data in (data.get("values") or {}).items():
            value = _value_from_json(value_data)
            dev_eui = cached_value_devices.get(entity_key, "")
            self.values[entity_key] = value
        self.entity_platforms = {
            entity_key: platform
            for entity_key, platform in (data.get("entity_platforms") or {}).items()
            if entity_key in self.values
        }
        self.value_devices = {}
        for entity_key, dev_eui in cached_value_devices.items():
            device = self.devices.get(dev_eui)
            if device is not None and entity_key in self.values:
                self.value_devices[entity_key] = device
        self.last_message_at = data.get("last_message_at")
        self.last_topic = data.get("last_topic")
        self.recent_messages = deque(data.get("recent_messages") or [], maxlen=10)
        self.last_downlink_by_device = dict(data.get("last_downlink_by_device") or {})
        self.next_downlink_by_device = dict(data.get("next_downlink_by_device") or {})

    async def async_save_cache(self) -> None:
        """Persist the latest devices and values for restart recovery."""
        await self._store.async_save(
            {
                "devices": {
                    dev_eui: _device_to_json(device)
                    for dev_eui, device in self.devices.items()
                },
                "values": {
                    entity_key: _value_to_json(value)
                    for entity_key, value in self.values.items()
                },
                "value_devices": {
                    entity_key: device.dev_eui
                    for entity_key, device in self.value_devices.items()
                },
                "entity_platforms": dict(self.entity_platforms),
                "last_seen_by_device": dict(self.last_seen_by_device),
                "last_message_at": self.last_message_at,
                "last_topic": self.last_topic,
                "recent_messages": list(self.recent_messages),
                "last_downlink_by_device": self.last_downlink_by_device,
                "next_downlink_by_device": self.next_downlink_by_device,
            }
        )

    def status(self) -> dict[str, Any]:
        """Return MQTT and LoRaWAN receive status for the frontend panel."""
        return {
            "configured": bool(self.host),
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "ssl": self.use_ssl,
            "username": self.username,
            "has_password": bool(self.password),
            "topics": self.topic_filters,
            "last_error": self.last_error,
            "last_connected_at": self.last_connected_at,
            "last_disconnected_at": self.last_disconnected_at,
            "last_message_at": self.last_message_at,
            "last_topic": self.last_topic,
            "message_count": self.message_count,
            "unsupported_message_count": self.unsupported_message_count,
            "lns_counts": dict(self.lns_counts),
            "downlink_event_count": self.downlink_event_count,
            "downlink_event_counts": dict(self.downlink_event_counts),
            "last_downlink_event_at": self.last_downlink_event_at,
            "last_downlink_topic": self.last_downlink_topic,
            "device_count": len(self.devices),
            "entity_count": len(self.values),
            "offline_after_hours": self.offline_after_hours,
            "recent_messages": list(self.recent_messages),
        }


def add_runtime_listener(
    hass: HomeAssistant,
    signal: str,
    entry_id: str,
    add_entity: Callable[[str], None],
) -> UnsubscribeCallback:
    """Register a dispatcher listener for this config entry."""
    from homeassistant.helpers.dispatcher import async_dispatcher_connect

    @callback
    def _handle_add(received_entry_id: str, entity_key: str) -> None:
        if received_entry_id == entry_id:
            add_entity(entity_key)

    return async_dispatcher_connect(hass, signal, _handle_add)


def _utc_now() -> str:
    """Return the current UTC time in ISO format."""
    return datetime.now(UTC).isoformat()


def _downlink_event(topic: str) -> str | None:
    """Return the downlink lifecycle event represented by an MQTT topic."""
    parts = topic.split("/")
    if topic.startswith("v3/") and len(parts) >= 6 and parts[-2] == "down":
        return parts[-1].casefold()
    if topic.startswith("application/") and topic.endswith("/command/down"):
        return "command"
    if topic.startswith("application/") and "/event/" in topic:
        event = parts[-1].casefold()
        if event in {"ack", "txack", "nack", "failed"}:
            return event
    return None


def _parse_utc(value: str | None) -> datetime | None:
    """Parse an ISO timestamp as UTC."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _device_to_json(device: LoRaWANDevice) -> dict[str, Any]:
    """Serialize a LoRaWAN device."""
    return {
        "application_id": device.application_id,
        "application_name": device.application_name,
        "dev_eui": device.dev_eui,
        "device_id": device.device_id,
        "device_name": device.device_name,
        "device_type": device.device_type,
        "network": device.network,
    }


def _device_from_json(data: dict[str, Any]) -> LoRaWANDevice:
    """Deserialize a LoRaWAN device."""
    return LoRaWANDevice(
        application_id=data["application_id"],
        application_name=data["application_name"],
        dev_eui=data["dev_eui"],
        device_id=data["device_id"],
        device_name=data["device_name"],
        device_type=data.get("device_type"),
        network=data.get("network", ""),
    )


def _value_to_json(value: LoRaWANValue) -> dict[str, Any]:
    """Serialize one LoRaWAN value."""
    return {
        "key": value.key,
        "name": value.name,
        "value": value.value,
        "raw_key": value.raw_key,
        "attributes": value.attributes,
    }


def _value_from_json(data: dict[str, Any]) -> LoRaWANValue:
    """Deserialize one LoRaWAN value."""
    return LoRaWANValue(
        key=data["key"],
        name=data["name"],
        value=data.get("value"),
        raw_key=data["raw_key"],
        attributes=data.get("attributes") or {},
    )


def _is_diagnostic_value(value: LoRaWANValue) -> bool:
    """Return true for raw/remaining diagnostic values."""
    return value.key.startswith("raw_") or value.key.startswith("remaining_")


def _clean_dev_eui(value: str) -> str:
    """Normalize a DevEUI for config lookups."""
    return str(value or "").replace(":", "").replace("-", "").upper()
