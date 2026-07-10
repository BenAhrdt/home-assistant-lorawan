"""Constants for the LoRaWAN integration."""

from __future__ import annotations

DOMAIN = "lorawan"

PLATFORMS = ["sensor", "binary_sensor"]

CONF_CREATE_RAW_SENSORS = "create_raw_sensors"
CONF_DEVICE_OFFLINE_AFTER_HOURS = "device_offline_after_hours"
CONF_OFFLINE_AFTER_HOURS = "offline_after_hours"
CONF_SSL = "ssl"

DEFAULT_NAME = "LoRaWAN"
DEFAULT_MQTT_PORT = 1883
DEFAULT_OFFLINE_AFTER_HOURS = 25

DEFAULT_TOPIC_FILTERS = [
    "v3/+/devices/+/+",
    "application/+/device/+/event/+",
]

SIGNAL_ADD_SENSOR = f"{DOMAIN}_add_sensor"
SIGNAL_ADD_BINARY_SENSOR = f"{DOMAIN}_add_binary_sensor"
SIGNAL_DEVICE_ADDED = f"{DOMAIN}_device_added"
SIGNAL_UPDATE_ENTITY = f"{DOMAIN}_update_entity"
