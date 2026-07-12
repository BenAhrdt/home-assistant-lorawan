"""Constants for the LoRaWAN integration."""

from __future__ import annotations

DOMAIN = "lorawan"

PLATFORMS = ["sensor", "binary_sensor", "number", "select", "switch", "button", "text"]

CONF_CREATE_RAW_SENSORS = "create_raw_sensors"
CONF_CREATE_REMAINING_SENSORS = "create_remaining_sensors"
CONF_DEVICE_OFFLINE_AFTER_HOURS = "device_offline_after_hours"
CONF_DEVICE_CREATE_RAW_SENSORS = "device_create_raw_sensors"
CONF_DEVICE_CREATE_REMAINING_SENSORS = "device_create_remaining_sensors"
CONF_DEVICE_TILE_VALUES = "device_tile_values"
CONF_DOWNLINK_PROFILES = "downlink_profiles"
CONF_OFFLINE_AFTER_HOURS = "offline_after_hours"
CONF_SSL = "ssl"
CONF_CONNECTION_COLOR = "connection_color"

DEFAULT_NAME = "LoRaWAN"
DEFAULT_MQTT_PORT = 1883
DEFAULT_OFFLINE_AFTER_HOURS = 25
DEFAULT_CONNECTION_COLOR = [3, 169, 244]

DEFAULT_TOPIC_FILTERS = [
    "v3/+/devices/+/+",
    "v3/+/devices/+/down/+",
    "application/+/device/+/event/+",
    "application/+/device/+/command/down",
]

SIGNAL_ADD_SENSOR = f"{DOMAIN}_add_sensor"
SIGNAL_ADD_BINARY_SENSOR = f"{DOMAIN}_add_binary_sensor"
SIGNAL_ADD_DOWNLINK_CONTROL = f"{DOMAIN}_add_downlink_control"
SIGNAL_REMOVE_DOWNLINK_CONTROL = f"{DOMAIN}_remove_downlink_control"
SIGNAL_DEVICE_ADDED = f"{DOMAIN}_device_added"
SIGNAL_UPDATE_ENTITY = f"{DOMAIN}_update_entity"
SIGNAL_UPDATE_DOWNLINK_CONTROLS = f"{DOMAIN}_update_downlink_controls"
