"""Config flow for the LoRaWAN integration."""

from __future__ import annotations

import asyncio
import colorsys
import uuid

import voluptuous as vol
from paho.mqtt import client as mqtt_client

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.helpers.selector import ColorRGBSelector

from .const import (
    CONF_CREATE_RAW_SENSORS,
    CONF_CONNECTION_COLOR,
    CONF_CREATE_REMAINING_SENSORS,
    CONF_DEVICE_CREATE_RAW_SENSORS,
    CONF_DEVICE_CREATE_REMAINING_SENSORS,
    CONF_DEVICE_OFFLINE_AFTER_HOURS,
    CONF_DOWNLINK_PROFILES,
    CONF_OFFLINE_AFTER_HOURS,
    CONF_SSL,
    DEFAULT_MQTT_PORT,
    DEFAULT_CONNECTION_COLOR,
    DEFAULT_NAME,
    DEFAULT_OFFLINE_AFTER_HOURS,
    DOMAIN,
)


class LoRaWANConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LoRaWAN."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create a LoRaWAN config entry."""
        errors = {}
        if user_input is not None:
            if await _async_test_mqtt_connection(user_input):
                await self.async_set_unique_id(user_input[CONF_NAME].lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=_entry_title(
                        user_input[CONF_NAME], user_input[CONF_CONNECTION_COLOR]
                    ),
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_SSL: user_input[CONF_SSL],
                        CONF_CONNECTION_COLOR: user_input[CONF_CONNECTION_COLOR],
                        CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
                        CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
                        CONF_CREATE_RAW_SENSORS: user_input[CONF_CREATE_RAW_SENSORS],
                        CONF_CREATE_REMAINING_SENSORS: user_input[
                            CONF_CREATE_REMAINING_SENSORS
                        ],
                        CONF_OFFLINE_AFTER_HOURS: user_input[
                            CONF_OFFLINE_AFTER_HOURS
                        ],
                        CONF_DEVICE_OFFLINE_AFTER_HOURS: {},
                        CONF_DEVICE_CREATE_RAW_SENSORS: {},
                        CONF_DEVICE_CREATE_REMAINING_SENSORS: {},
                        CONF_DOWNLINK_PROFILES: [],
                    },
                )
            errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): vol.All(str, vol.Length(min=1)),
                vol.Required(CONF_PORT, default=DEFAULT_MQTT_PORT): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=65535),
                ),
                vol.Required(CONF_SSL, default=False): bool,
                vol.Required(
                    CONF_CONNECTION_COLOR,
                    default=DEFAULT_CONNECTION_COLOR,
                ): ColorRGBSelector(),
                vol.Optional(CONF_USERNAME, default=""): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
                vol.Required(CONF_CREATE_RAW_SENSORS, default=True): bool,
                vol.Required(CONF_CREATE_REMAINING_SENSORS, default=False): bool,
                vol.Required(
                    CONF_OFFLINE_AFTER_HOURS,
                    default=DEFAULT_OFFLINE_AFTER_HOURS,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=8760),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return LoRaWANOptionsFlow(config_entry)


class LoRaWANOptionsFlow(config_entries.OptionsFlow):
    """Handle LoRaWAN options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage LoRaWAN options."""
        current = dict(self._config_entry.data)
        current.update(self._config_entry.options)
        errors = {}

        if user_input is not None:
            if await _async_test_mqtt_connection(user_input):
                data = {
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_SSL: user_input[CONF_SSL],
                    CONF_CONNECTION_COLOR: user_input[CONF_CONNECTION_COLOR],
                    CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
                    CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
                    CONF_CREATE_RAW_SENSORS: user_input[CONF_CREATE_RAW_SENSORS],
                    CONF_CREATE_REMAINING_SENSORS: user_input[
                        CONF_CREATE_REMAINING_SENSORS
                    ],
                    CONF_OFFLINE_AFTER_HOURS: user_input[CONF_OFFLINE_AFTER_HOURS],
                    CONF_DEVICE_OFFLINE_AFTER_HOURS: current.get(
                        CONF_DEVICE_OFFLINE_AFTER_HOURS,
                        {},
                    ),
                    CONF_DEVICE_CREATE_RAW_SENSORS: current.get(
                        CONF_DEVICE_CREATE_RAW_SENSORS,
                        {},
                    ),
                    CONF_DEVICE_CREATE_REMAINING_SENSORS: current.get(
                        CONF_DEVICE_CREATE_REMAINING_SENSORS,
                        {},
                    ),
                    CONF_DOWNLINK_PROFILES: current.get(CONF_DOWNLINK_PROFILES, []),
                }
                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    title=_entry_title(
                        user_input[CONF_NAME], user_input[CONF_CONNECTION_COLOR]
                    ),
                    data=data,
                    options={},
                )
                return self.async_create_entry(title="", data={})
            errors["base"] = "cannot_connect"

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=current.get(CONF_NAME, self._config_entry.title),
                ): str,
                vol.Required(
                    CONF_HOST,
                    default=current.get(CONF_HOST, ""),
                ): vol.All(str, vol.Length(min=1)),
                vol.Required(
                    CONF_PORT,
                    default=current.get(CONF_PORT, DEFAULT_MQTT_PORT),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=65535),
                ),
                vol.Required(CONF_SSL, default=current.get(CONF_SSL, False)): bool,
                vol.Required(
                    CONF_CONNECTION_COLOR,
                    default=current.get(
                        CONF_CONNECTION_COLOR,
                        DEFAULT_CONNECTION_COLOR,
                    ),
                ): ColorRGBSelector(),
                vol.Optional(
                    CONF_USERNAME,
                    default=current.get(CONF_USERNAME, ""),
                ): str,
                vol.Optional(
                    CONF_PASSWORD,
                    default=current.get(CONF_PASSWORD, ""),
                ): str,
                vol.Required(
                    CONF_CREATE_RAW_SENSORS,
                    default=current.get(CONF_CREATE_RAW_SENSORS, True),
                ): bool,
                vol.Required(
                    CONF_CREATE_REMAINING_SENSORS,
                    default=current.get(
                        CONF_CREATE_REMAINING_SENSORS,
                        False,
                    ),
                ): bool,
                vol.Required(
                    CONF_OFFLINE_AFTER_HOURS,
                    default=current.get(
                        CONF_OFFLINE_AFTER_HOURS,
                        DEFAULT_OFFLINE_AFTER_HOURS,
                    ),
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=8760),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )


async def _async_test_mqtt_connection(config: dict) -> bool:
    """Test MQTT authentication without subscribing or changing runtime state."""
    loop = asyncio.get_running_loop()
    connected = loop.create_future()
    client = mqtt_client.Client(
        client_id=f"home-assistant-lorawan-test-{uuid.uuid4().hex}"
    )

    def on_connect(client, userdata, flags, result_code, *args):
        del client, userdata, flags, args
        def resolve() -> None:
            if not connected.done():
                connected.set_result(int(result_code) == 0)

        loop.call_soon_threadsafe(resolve)

    client.on_connect = on_connect
    username = config.get(CONF_USERNAME, "")
    if username:
        client.username_pw_set(username, config.get(CONF_PASSWORD) or None)
    if config.get(CONF_SSL, False):
        client.tls_set()

    try:
        client.connect_async(config[CONF_HOST], config[CONF_PORT], keepalive=15)
        client.loop_start()
        return await asyncio.wait_for(connected, timeout=10)
    except (OSError, ValueError, asyncio.TimeoutError):
        return False
    finally:
        client.disconnect()
        client.loop_stop()


def _entry_title(name: str, color: list[int]) -> str:
    """Prefix a config-entry title with a stable color-family emoji."""
    red, green, blue = (max(0, min(255, int(channel))) / 255 for channel in color)
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    hue *= 360
    if value < 0.2:
        emoji = "⬛"
    elif saturation < 0.12:
        emoji = "⬜" if value > 0.75 else "⬛"
    elif value < 0.55 and (hue < 55 or hue >= 345):
        emoji = "🟫"
    elif hue < 15 or hue >= 345:
        emoji = "🟥"
    elif hue < 50:
        emoji = "🟧"
    elif hue < 75:
        emoji = "🟨"
    elif hue < 170:
        emoji = "🟩"
    elif hue < 260:
        emoji = "🟦"
    else:
        emoji = "🟪"
    return f"{emoji} {name.strip()}"
