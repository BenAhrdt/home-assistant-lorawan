"""LoRaWAN integration."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    CONF_DEVICE_OFFLINE_AFTER_HOURS,
    CONF_OFFLINE_AFTER_HOURS,
    CONF_SSL,
    DEFAULT_MQTT_PORT,
    DEFAULT_OFFLINE_AFTER_HOURS,
    DEFAULT_TOPIC_FILTERS,
    DOMAIN,
    PLATFORMS,
    SIGNAL_DEVICE_ADDED,
)
from .runtime import LoRaWANRuntime

PANEL_STATIC_URL = "/lorawan_static"
SERVICE_CONFIGURE_MQTT = "configure_mqtt"
SERVICE_CONFIGURE_DEVICE = "configure_device"
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the LoRaWAN sidebar panel."""
    async def async_configure_mqtt_service(call: ServiceCall) -> None:
        await _async_configure_mqtt(hass, call)

    async def async_configure_device_service(call: ServiceCall) -> None:
        await _async_configure_device(hass, call)

    frontend_path = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_STATIC_URL, str(frontend_path), False)]
    )
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="LoRaWAN",
        sidebar_icon="mdi:radio-tower",
        frontend_url_path=DOMAIN,
        config={
            "_panel_custom": {
                "name": "lorawan-panel",
                "module_url": f"{PANEL_STATIC_URL}/panel.js",
                "embed_iframe": False,
            }
        },
        require_admin=True,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CONFIGURE_MQTT,
        async_configure_mqtt_service,
        schema=vol.Schema(
            {
                vol.Required(CONF_HOST): vol.All(str, vol.Length(min=1)),
                vol.Required(CONF_PORT, default=DEFAULT_MQTT_PORT): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=65535),
                ),
                vol.Required(CONF_SSL, default=False): bool,
                vol.Optional(CONF_USERNAME, default=""): str,
                vol.Optional(CONF_PASSWORD): str,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CONFIGURE_DEVICE,
        async_configure_device_service,
        schema=vol.Schema(
            {
                vol.Required("dev_eui"): vol.All(str, vol.Length(min=1)),
                vol.Required(CONF_OFFLINE_AFTER_HOURS): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=8760),
                ),
            }
        ),
    )
    websocket_api.async_register_command(hass, _websocket_status)
    websocket_api.async_register_command(hass, _websocket_devices)
    websocket_api.async_register_command(hass, _websocket_subscribe_devices)
    return True


async def _async_configure_mqtt(hass: HomeAssistant, call: ServiceCall) -> None:
    """Update MQTT connection settings from the sidebar panel."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        _LOGGER.warning("Cannot configure LoRaWAN MQTT because no config entry exists")
        return

    entry = entries[0]
    data = dict(entry.data)
    data.update(
        {
            CONF_HOST: call.data[CONF_HOST],
            CONF_PORT: call.data[CONF_PORT],
            CONF_SSL: call.data[CONF_SSL],
            CONF_USERNAME: call.data.get(CONF_USERNAME, ""),
        }
    )
    if CONF_PASSWORD in call.data:
        data[CONF_PASSWORD] = call.data[CONF_PASSWORD]
    elif not call.data.get(CONF_USERNAME):
        data[CONF_PASSWORD] = ""
    hass.config_entries.async_update_entry(entry, data=data)


async def _async_configure_device(hass: HomeAssistant, call: ServiceCall) -> None:
    """Update per-device LoRaWAN settings from the sidebar panel."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        _LOGGER.warning("Cannot configure LoRaWAN device because no config entry exists")
        return

    entry = entries[0]
    data = dict(entry.data)
    overrides = dict(data.get(CONF_DEVICE_OFFLINE_AFTER_HOURS) or {})
    overrides[_clean_dev_eui(call.data["dev_eui"])] = call.data[CONF_OFFLINE_AFTER_HOURS]
    data[CONF_DEVICE_OFFLINE_AFTER_HOURS] = overrides
    hass.config_entries.async_update_entry(entry, data=data)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/status"})
@websocket_api.async_response
async def _websocket_status(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Return LoRaWAN status for the sidebar panel."""
    entries = hass.config_entries.async_entries(DOMAIN)
    runtime = None
    if entries:
        runtime = hass.data.get(DOMAIN, {}).get(entries[0].entry_id)

    if runtime is None:
        connection.send_result(
            msg["id"],
            _config_entry_status(entries[0] if entries else None),
        )
        return

    connection.send_result(msg["id"], runtime.status())


def _config_entry_status(entry: ConfigEntry | None) -> dict:
    """Return persisted LoRaWAN settings when the runtime is not available."""
    data = dict(entry.data) if entry is not None else {}
    return {
        "configured": bool(data.get(CONF_HOST)),
        "connected": False,
        "host": data.get(CONF_HOST, ""),
        "port": data.get(CONF_PORT, DEFAULT_MQTT_PORT),
        "ssl": data.get(CONF_SSL, False),
        "username": data.get(CONF_USERNAME, ""),
        "has_password": bool(data.get(CONF_PASSWORD)),
        "topics": list(DEFAULT_TOPIC_FILTERS),
        "message_count": 0,
        "unsupported_message_count": 0,
        "lns_counts": {"ttn": 0, "chirpstack": 0},
        "device_count": 0,
        "entity_count": 0,
        "offline_after_hours": data.get(
            CONF_OFFLINE_AFTER_HOURS,
            DEFAULT_OFFLINE_AFTER_HOURS,
        ),
    }


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/devices"})
@websocket_api.async_response
async def _websocket_devices(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Return LoRaWAN devices from the Home Assistant registries."""
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    entity_counts: dict[str, int] = {}
    for entity in entity_registry.entities.values():
        if entity.device_id is None:
            continue
        entity_counts[entity.device_id] = entity_counts.get(entity.device_id, 0) + 1

    devices = []
    entries = hass.config_entries.async_entries(DOMAIN)
    config = dict(entries[0].data) if entries else {}
    default_offline_after = config.get(
        CONF_OFFLINE_AFTER_HOURS,
        DEFAULT_OFFLINE_AFTER_HOURS,
    )
    offline_overrides = {
        _clean_dev_eui(dev_eui): hours
        for dev_eui, hours in (
            config.get(CONF_DEVICE_OFFLINE_AFTER_HOURS) or {}
        ).items()
    }
    for device in device_registry.devices.values():
        identifiers = {
            identifier
            for domain, identifier in device.identifiers
            if domain == DOMAIN
        }
        if not identifiers:
            continue

        dev_eui = next(iter(identifiers))
        devices.append(
            {
                "id": device.id,
                "name": device.name_by_user or device.name or dev_eui,
                "model": device.model,
                "manufacturer": device.manufacturer,
                "sw_version": device.sw_version,
                "identifiers": sorted(identifiers),
                "entity_count": entity_counts.get(device.id, 0),
                "offline_after_hours": offline_overrides.get(
                    _clean_dev_eui(dev_eui),
                    default_offline_after,
                ),
                "offline_after_default_hours": default_offline_after,
            }
        )

    devices.sort(key=lambda item: item["name"].lower())
    connection.send_result(msg["id"], {"devices": devices})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/subscribe_devices"})
@websocket_api.async_response
async def _websocket_subscribe_devices(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Subscribe the frontend to LoRaWAN device changes."""

    @callback
    def async_device_added(entry_id: str, dev_eui: str) -> None:
        connection.send_event(
            msg["id"],
            {
                "event": "device_added",
                "entry_id": entry_id,
                "dev_eui": dev_eui,
            },
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass,
        SIGNAL_DEVICE_ADDED,
        async_device_added,
    )
    connection.send_result(msg["id"])


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LoRaWAN from a config entry."""
    runtime = LoRaWANRuntime(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime

    await runtime.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_entry))
    return True


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload LoRaWAN when config entry options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a LoRaWAN config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    runtime: LoRaWANRuntime | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if runtime is not None:
        await runtime.async_stop()
    return unload_ok


def _clean_dev_eui(value: str) -> str:
    """Normalize a DevEUI for config storage."""
    return str(value or "").replace(":", "").replace("-", "").upper()
