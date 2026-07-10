"""Config flow for the LoRaWAN integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)

from .const import (
    CONF_CREATE_RAW_SENSORS,
    CONF_DEVICE_OFFLINE_AFTER_HOURS,
    CONF_OFFLINE_AFTER_HOURS,
    CONF_SSL,
    DEFAULT_MQTT_PORT,
    DEFAULT_NAME,
    DEFAULT_OFFLINE_AFTER_HOURS,
    DOMAIN,
)


class LoRaWANConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LoRaWAN."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create a LoRaWAN config entry."""
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_NAME].lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_SSL: user_input[CONF_SSL],
                    CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
                    CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
                    CONF_CREATE_RAW_SENSORS: user_input[CONF_CREATE_RAW_SENSORS],
                    CONF_OFFLINE_AFTER_HOURS: user_input[CONF_OFFLINE_AFTER_HOURS],
                    CONF_DEVICE_OFFLINE_AFTER_HOURS: {},
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): vol.All(str, vol.Length(min=1)),
                vol.Required(CONF_PORT, default=DEFAULT_MQTT_PORT): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=65535),
                ),
                vol.Required(CONF_SSL, default=False): bool,
                vol.Optional(CONF_USERNAME, default=""): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
                vol.Required(CONF_CREATE_RAW_SENSORS, default=True): bool,
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

        if user_input is not None:
            data = {
                CONF_NAME: user_input[CONF_NAME],
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_SSL: user_input[CONF_SSL],
                CONF_USERNAME: user_input.get(CONF_USERNAME, ""),
                CONF_PASSWORD: user_input.get(CONF_PASSWORD, ""),
                CONF_CREATE_RAW_SENSORS: user_input[CONF_CREATE_RAW_SENSORS],
                CONF_OFFLINE_AFTER_HOURS: user_input[CONF_OFFLINE_AFTER_HOURS],
                CONF_DEVICE_OFFLINE_AFTER_HOURS: current.get(
                    CONF_DEVICE_OFFLINE_AFTER_HOURS,
                    {},
                ),
            }
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                title=user_input[CONF_NAME],
                data=data,
                options={},
            )
            return self.async_create_entry(title="", data={})

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
        )
