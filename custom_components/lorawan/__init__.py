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
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    CONF_DEVICE_OFFLINE_AFTER_HOURS,
    CONF_DOWNLINK_PROFILES,
    CONF_DEVICE_CREATE_RAW_SENSORS,
    CONF_DEVICE_CREATE_REMAINING_SENSORS,
    CONF_CREATE_RAW_SENSORS,
    CONF_CREATE_REMAINING_SENSORS,
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
from .downlinks import BUILTIN_PROFILES, merged_profiles, parameter_payload, profile_for_device

PANEL_STATIC_URL = "/lorawan_static"
SERVICE_CONFIGURE_MQTT = "configure_mqtt"
SERVICE_CONFIGURE_DEVICE = "configure_device"
SERVICE_CONFIGURE_DOWNLINK_PROFILES = "configure_downlink_profiles"
_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the LoRaWAN sidebar panel."""
    async def async_configure_mqtt_service(call: ServiceCall) -> None:
        await _async_configure_mqtt(hass, call)

    async def async_configure_device_service(call: ServiceCall) -> None:
        await _async_configure_device(hass, call)

    async def async_configure_downlink_profiles_service(call: ServiceCall) -> None:
        await _async_configure_downlink_profiles(hass, call)

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
        SERVICE_CONFIGURE_DOWNLINK_PROFILES,
        async_configure_downlink_profiles_service,
        schema=vol.Schema({vol.Required(CONF_DOWNLINK_PROFILES): list}),
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
                vol.Required(CONF_CREATE_RAW_SENSORS): bool,
                vol.Required(CONF_CREATE_REMAINING_SENSORS): bool,
            }
        ),
    )
    websocket_api.async_register_command(hass, _websocket_status)
    websocket_api.async_register_command(hass, _websocket_devices)
    websocket_api.async_register_command(hass, _websocket_device_diagnostics)
    websocket_api.async_register_command(hass, _websocket_subscribe_devices)
    websocket_api.async_register_command(hass, _websocket_downlinks)
    websocket_api.async_register_command(hass, _websocket_send_downlink)
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
    raw_overrides = dict(data.get(CONF_DEVICE_CREATE_RAW_SENSORS) or {})
    raw_overrides[_clean_dev_eui(call.data["dev_eui"])] = call.data[
        CONF_CREATE_RAW_SENSORS
    ]
    data[CONF_DEVICE_CREATE_RAW_SENSORS] = raw_overrides
    remaining_overrides = dict(data.get(CONF_DEVICE_CREATE_REMAINING_SENSORS) or {})
    remaining_overrides[_clean_dev_eui(call.data["dev_eui"])] = call.data[
        CONF_CREATE_REMAINING_SENSORS
    ]
    data[CONF_DEVICE_CREATE_REMAINING_SENSORS] = remaining_overrides
    hass.config_entries.async_update_entry(entry, data=data)


async def _async_configure_downlink_profiles(hass: HomeAssistant, call: ServiceCall) -> None:
    """Persist user-defined downlink profiles."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return
    entry = entries[0]
    data = dict(entry.data)
    data[CONF_DOWNLINK_PROFILES] = call.data[CONF_DOWNLINK_PROFILES]
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
        "recent_messages": [],
    }


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/downlinks"})
@websocket_api.async_response
async def _websocket_downlinks(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Return devices and available downlink profiles for the panel."""
    entries = hass.config_entries.async_entries(DOMAIN)
    entry = entries[0] if entries else None
    data = dict(entry.data) if entry else {}
    runtime: LoRaWANRuntime | None = hass.data.get(DOMAIN, {}).get(entry.entry_id) if entry else None
    devices = []
    if runtime is not None:
        devices = [
            {
                "dev_eui": device.dev_eui,
                "name": device.device_name or device.device_id or device.dev_eui,
                "device_type": device.device_type or "",
                "network": _network_for_device(device),
            }
            for device in runtime.devices.values()
        ]
    configured_profiles = data.get(CONF_DOWNLINK_PROFILES, [])
    connection.send_result(
        msg["id"],
        {
            "devices": devices,
            "profiles": merged_profiles(configured_profiles),
            "configured_profiles": configured_profiles,
            "builtin_profile_types": [profile["deviceType"] for profile in BUILTIN_PROFILES],
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/send_downlink",
        vol.Required("dev_eui"): str,
        vol.Required("device_type"): str,
        vol.Required("parameter_name"): str,
        vol.Required("value"): object,
    }
)
@websocket_api.async_response
async def _websocket_send_downlink(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Create and publish one downlink selected in the panel."""
    entries = hass.config_entries.async_entries(DOMAIN)
    runtime: LoRaWANRuntime | None = None
    entry = entries[0] if entries else None
    if entry:
        runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if runtime is None:
        connection.send_error(msg["id"], "not_ready", "LoRaWAN ist nicht bereit")
        return
    device = runtime.devices.get(_clean_dev_eui(msg["dev_eui"]))
    profile = profile_for_device(merged_profiles(entry.data.get(CONF_DOWNLINK_PROFILES)), msg["device_type"])
    if device is None or profile is None:
        connection.send_error(msg["id"], "not_found", "Gerät oder Downlink-Profil nicht gefunden")
        return
    parameter = next((item for item in profile.get("downlinkParameter", []) if item.get("name") == msg["parameter_name"]), None)
    if parameter is None:
        connection.send_error(msg["id"], "not_found", "Downlink-Parameter nicht gefunden")
        return
    try:
        payload = parameter_payload(parameter, msg["value"])
        runtime.send_downlink(_network_for_device(device), device, {**profile, **parameter}, payload)
    except (RuntimeError, ValueError) as err:
        connection.send_error(msg["id"], "send_failed", str(err))
        return
    connection.send_result(msg["id"], {"payload_hex": payload})


def _network_for_device(device) -> str:
    """Infer the LNS format from its application identifier."""
    return device.network or ("ttn" if "@" in device.application_name else "chirpstack")


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/devices"})
@websocket_api.async_response
async def _websocket_devices(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Return LoRaWAN devices from the Home Assistant registries."""
    device_registry = dr.async_get(hass)

    devices = []
    entries = hass.config_entries.async_entries(DOMAIN)
    config = dict(entries[0].data) if entries else {}
    runtime: LoRaWANRuntime | None = None
    if entries:
        runtime = hass.data.get(DOMAIN, {}).get(entries[0].entry_id)
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
    raw_overrides = {
        _clean_dev_eui(dev_eui): enabled
        for dev_eui, enabled in (
            config.get(CONF_DEVICE_CREATE_RAW_SENSORS) or {}
        ).items()
    }
    remaining_overrides = {
        _clean_dev_eui(dev_eui): enabled
        for dev_eui, enabled in (
            config.get(CONF_DEVICE_CREATE_REMAINING_SENSORS) or {}
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
        runtime_device = (
            runtime.devices.get(_clean_dev_eui(dev_eui)) if runtime else None
        )
        devices.append(
            {
                "id": device.id,
                "name": device.name_by_user or device.name or dev_eui,
                "model": device.model,
                "manufacturer": device.manufacturer,
                "sw_version": device.sw_version,
                "application_name": (
                    runtime_device.application_name if runtime_device else None
                ),
                "identifiers": sorted(identifiers),
                "online": runtime.is_device_online(dev_eui) if runtime else False,
                "offline_after_hours": offline_overrides.get(
                    _clean_dev_eui(dev_eui),
                    default_offline_after,
                ),
                "offline_after_default_hours": default_offline_after,
                "create_raw_sensors": raw_overrides.get(
                    _clean_dev_eui(dev_eui),
                    config.get(CONF_CREATE_RAW_SENSORS, True),
                ),
                "create_remaining_sensors": remaining_overrides.get(
                    _clean_dev_eui(dev_eui),
                    config.get(
                        CONF_CREATE_REMAINING_SENSORS,
                        False,
                    ),
                ),
            }
        )

    devices.sort(key=lambda item: item["name"].lower())
    connection.send_result(msg["id"], {"devices": devices})


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/device_diagnostics",
        vol.Required("dev_eui"): str,
    }
)
@websocket_api.async_response
async def _websocket_device_diagnostics(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict,
) -> None:
    """Return the latest diagnostic payloads for one LoRaWAN device."""
    entries = hass.config_entries.async_entries(DOMAIN)
    runtime: LoRaWANRuntime | None = None
    if entries:
        runtime = hass.data.get(DOMAIN, {}).get(entries[0].entry_id)
    if runtime is None:
        connection.send_result(msg["id"], {"raw": None, "remaining": None})
        return
    connection.send_result(msg["id"], runtime.diagnostics_for_device(msg["dev_eui"]))


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
    _remove_obsolete_remaining_entities(hass, entry)
    runtime = LoRaWANRuntime(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime

    await runtime.async_start()
    _remove_stale_downlink_entities(hass, entry, runtime)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_entry))
    return True


def _remove_stale_downlink_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
    runtime: LoRaWANRuntime,
) -> None:
    """Remove registered downlink controls that no longer match a device profile."""
    runtime.downlink_controls_for_platform("number")
    valid_unique_ids = set(runtime.downlink_controls)
    registry = er.async_get(hass)
    prefix = f"{entry.entry_id}_"
    for entity in list(registry.entities.values()):
        if (
            entity.config_entry_id == entry.entry_id
            and entity.unique_id.startswith(prefix)
            and "_downlink_" in entity.unique_id
            and "_downlink_next_send" not in entity.unique_id
            and "_downlink_last_send_" not in entity.unique_id
            and entity.unique_id not in valid_unique_ids
        ):
            registry.async_remove(entity.entity_id)


async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload LoRaWAN when config entry options change."""
    _sync_diagnostic_entity_status(hass, entry)
    await hass.config_entries.async_reload(entry.entry_id)


def _sync_diagnostic_entity_status(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Enable or disable existing diagnostic entities from the configuration."""
    data = dict(entry.data)
    raw_overrides = data.get(CONF_DEVICE_CREATE_RAW_SENSORS) or {}
    remaining_overrides = data.get(CONF_DEVICE_CREATE_REMAINING_SENSORS) or {}
    registry = er.async_get(hass)
    prefix = f"{entry.entry_id}_"
    for entity in list(registry.entities.values()):
        if not entity.unique_id.startswith(prefix):
            continue
        dev_eui, _, value_key = entity.unique_id[len(prefix) :].partition("_")
        if value_key.startswith("raw_") or value_key.startswith("downlink_raw_"):
            enabled = raw_overrides.get(
                _clean_dev_eui(dev_eui), data.get(CONF_CREATE_RAW_SENSORS, True)
            )
        elif value_key.startswith("remaining_"):
            enabled = remaining_overrides.get(
                _clean_dev_eui(dev_eui),
                data.get(
                    CONF_CREATE_REMAINING_SENSORS,
                    False,
                ),
            )
        else:
            continue
        disabled_by = None if enabled else er.RegistryEntryDisabler.INTEGRATION
        if entity.disabled_by != disabled_by:
            registry.async_update_entity(entity.entity_id, disabled_by=disabled_by)


def _remove_obsolete_remaining_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove the obsolete combined remaining-payload entity from the registry."""
    registry = er.async_get(hass)
    prefix = f"{entry.entry_id}_"
    for entity in list(registry.entities.values()):
        if not entity.unique_id.startswith(prefix):
            continue
        _, _, value_key = entity.unique_id[len(prefix) :].partition("_")
        if value_key in {"remaining_json", "downlink_last_send_json"}:
            registry.async_remove(entity.entity_id)


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
