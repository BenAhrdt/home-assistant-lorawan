"""LoRaWAN integration."""

from __future__ import annotations

import colorsys
import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (
    CONF_DEVICE_OFFLINE_AFTER_HOURS,
    CONF_CONNECTION_COLOR,
    CONF_DOWNLINK_PROFILES,
    CONF_DEVICE_CREATE_RAW_SENSORS,
    CONF_DEVICE_CREATE_REMAINING_SENSORS,
    CONF_DEVICE_TILE_VALUES,
    CONF_DEVICE_CLIMATE_ENTITIES,
    CONF_CREATE_RAW_SENSORS,
    CONF_CREATE_REMAINING_SENSORS,
    CONF_OFFLINE_AFTER_HOURS,
    CONF_SSL,
    DEFAULT_MQTT_PORT,
    DEFAULT_CONNECTION_COLOR,
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
                "module_url": f"{PANEL_STATIC_URL}/panel.js?v=0.1.19",
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
                vol.Optional("entry_id"): str,
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
                vol.Optional("entry_id"): str,
                vol.Required(CONF_OFFLINE_AFTER_HOURS): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1, max=8760),
                ),
                vol.Required(CONF_CREATE_RAW_SENSORS): bool,
                vol.Required(CONF_CREATE_REMAINING_SENSORS): bool,
                vol.Required(CONF_DEVICE_TILE_VALUES): [str],
                vol.Optional(CONF_DEVICE_CLIMATE_ENTITIES): [dict],
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

    requested_entry_id = call.data.get("entry_id")
    entry = next(
        (item for item in entries if item.entry_id == requested_entry_id),
        entries[0],
    )
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

    requested_entry_id = call.data.get("entry_id")
    entry = next(
        (item for item in entries if item.entry_id == requested_entry_id),
        entries[0],
    )
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
    tile_value_overrides = dict(data.get(CONF_DEVICE_TILE_VALUES) or {})
    tile_value_overrides[_clean_dev_eui(call.data["dev_eui"])] = list(
        call.data[CONF_DEVICE_TILE_VALUES]
    )
    data[CONF_DEVICE_TILE_VALUES] = tile_value_overrides
    if CONF_DEVICE_CLIMATE_ENTITIES in call.data:
        climate_overrides = dict(data.get(CONF_DEVICE_CLIMATE_ENTITIES) or {})
        climate_overrides[_clean_dev_eui(call.data["dev_eui"])] = list(
            call.data[CONF_DEVICE_CLIMATE_ENTITIES]
        )
        data[CONF_DEVICE_CLIMATE_ENTITIES] = climate_overrides
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
    runtimes = hass.data.get(DOMAIN, {})
    statuses = []
    for index, entry in enumerate(entries):
        runtime = runtimes.get(entry.entry_id)
        status = runtime.status() if runtime is not None else _config_entry_status(entry)
        statuses.append(
            {
                **status,
                "entry_id": entry.entry_id,
                "name": _entry_name(entry),
                "color": _connection_color(entry, index),
            }
        )

    connection.send_result(msg["id"], _aggregate_status(statuses))


def _aggregate_status(statuses: list[dict]) -> dict:
    """Return a backwards-compatible aggregate plus per-entry connection data."""
    recent_messages = sorted(
        (
            {**message, "entry_id": status["entry_id"], "connection_name": status["name"]}
            for status in statuses
            for message in status.get("recent_messages", [])
        ),
        key=lambda message: message.get("received_at", ""),
        reverse=True,
    )[:10]
    protocol_events = sorted(
        (
            {
                **event,
                "entry_id": status["entry_id"],
                "connection_name": status["name"],
                "connection_color": status["color"],
            }
            for status in statuses
            for event in status.get("protocol_events", [])
        ),
        key=lambda event: event.get("timestamp", ""),
        reverse=True,
    )[:500]
    return {
        "configured": any(status.get("configured") for status in statuses),
        "connected": any(status.get("connected") for status in statuses),
        "connections": statuses,
        "message_count": sum(status.get("message_count", 0) for status in statuses),
        "unsupported_message_count": sum(
            status.get("unsupported_message_count", 0) for status in statuses
        ),
        "lns_counts": {
            network: sum(
                status.get("lns_counts", {}).get(network, 0) for status in statuses
            )
            for network in ("ttn", "chirpstack")
        },
        "downlink_event_count": sum(
            status.get("downlink_event_count", 0) for status in statuses
        ),
        "device_count": sum(status.get("device_count", 0) for status in statuses),
        "entity_count": sum(status.get("entity_count", 0) for status in statuses),
        "recent_messages": recent_messages,
        "protocol_events": protocol_events,
    }


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
        "downlink_event_count": 0,
        "downlink_event_counts": {},
        "device_count": 0,
        "entity_count": 0,
        "offline_after_hours": data.get(
            CONF_OFFLINE_AFTER_HOURS,
            DEFAULT_OFFLINE_AFTER_HOURS,
        ),
        "recent_messages": [],
        "protocol_events": [],
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
    """Return LoRaWAN devices, using the MQTT runtimes as primary source."""
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    entries = hass.config_entries.async_entries(DOMAIN)
    entries_by_id = {entry.entry_id: entry for entry in entries}
    entry_indexes = {entry.entry_id: index for index, entry in enumerate(entries)}
    runtimes = hass.data.get(DOMAIN, {})

    registry_by_eui = {}
    for device in device_registry.devices.values():
        identifiers = _device_domain_identifiers(device.identifiers)
        for identifier in identifiers:
            registry_by_eui.setdefault(
                _clean_dev_eui(identifier), (device, identifiers)
            )

    devices = []
    included_registry_devices = set()
    for entry in entries:
        runtime: LoRaWANRuntime | None = runtimes.get(entry.entry_id)
        if runtime is None:
            continue
        for dev_eui, runtime_device in runtime.devices.items():
            clean_dev_eui = _clean_dev_eui(dev_eui)
            registry_device, identifiers = registry_by_eui.get(
                clean_dev_eui, (None, {runtime_device.dev_eui})
            )
            if registry_device is not None:
                included_registry_devices.add(registry_device.id)
            try:
                payload = _panel_device_payload(
                    hass,
                    entity_registry,
                    registry_device,
                    identifiers,
                    entry,
                    entry_indexes[entry.entry_id],
                    runtime,
                    runtime_device,
                    clean_dev_eui,
                )
            except Exception:  # noqa: BLE001 - registry data must not hide runtime devices
                _LOGGER.exception(
                    "Failed to enrich LoRaWAN device %s from the registries",
                    runtime_device.dev_eui,
                )
                payload = _panel_device_payload(
                    hass,
                    entity_registry,
                    None,
                    {runtime_device.dev_eui},
                    entry,
                    entry_indexes[entry.entry_id],
                    runtime,
                    runtime_device,
                    clean_dev_eui,
                )
            devices.append(payload)

    # Retain registry devices from older cached data even when their runtime is not
    # currently loaded. Runtime devices above never depend on this fallback path.
    for registry_device, identifiers in registry_by_eui.values():
        if registry_device.id in included_registry_devices:
            continue
        included_registry_devices.add(registry_device.id)
        entry_id = next(
            (
                candidate
                for candidate in registry_device.config_entries
                if candidate in entries_by_id
            ),
            None,
        )
        entry = entries_by_id.get(entry_id)
        dev_eui = next(iter(identifiers))
        try:
            payload = _panel_device_payload(
                hass,
                entity_registry,
                registry_device,
                identifiers,
                entry,
                entry_indexes.get(entry_id, 0),
                None,
                None,
                _clean_dev_eui(dev_eui),
            )
        except Exception:  # noqa: BLE001 - ignore broken stale registry entries
            _LOGGER.exception(
                "Failed to add stale LoRaWAN registry device %s",
                registry_device.id,
            )
            continue
        devices.append(payload)

    devices.sort(key=lambda item: item["name"].lower())
    connection.send_result(msg["id"], {"devices": devices})


def _device_domain_identifiers(registry_identifiers) -> set[str]:
    """Extract LoRaWAN identifiers from valid and extended registry tuples."""
    identifiers = set()
    for parts in registry_identifiers:
        if not isinstance(parts, (tuple, list)) or len(parts) < 2:
            continue
        domain, identifier = parts[0], parts[1]
        if domain == DOMAIN:
            identifiers.add(str(identifier))
    return identifiers


def _panel_device_payload(
    hass,
    entity_registry,
    registry_device,
    identifiers,
    entry,
    entry_index,
    runtime,
    runtime_device,
    clean_dev_eui,
) -> dict:
    """Build one JSON-safe device description for the sidebar panel."""
    config = dict(entry.data) if entry else {}
    default_offline_after = config.get(
        CONF_OFFLINE_AFTER_HOURS, DEFAULT_OFFLINE_AFTER_HOURS
    )
    offline_overrides = config.get(CONF_DEVICE_OFFLINE_AFTER_HOURS) or {}
    raw_overrides = config.get(CONF_DEVICE_CREATE_RAW_SENSORS) or {}
    remaining_overrides = config.get(CONF_DEVICE_CREATE_REMAINING_SENSORS) or {}
    tile_value_overrides = config.get(CONF_DEVICE_TILE_VALUES) or {}
    climate_overrides = config.get(CONF_DEVICE_CLIMATE_ENTITIES) or {}
    available_entities = _panel_device_entities(
        hass, entity_registry, registry_device.id if registry_device else None
    )
    selected_tile_values = tile_value_overrides.get(clean_dev_eui, [])
    entities_by_id = {value["entity_id"]: value for value in available_entities}
    dev_eui = runtime_device.dev_eui if runtime_device else next(iter(identifiers))
    return {
        "id": registry_device.id if registry_device else "",
        "name": str(
            (registry_device.name_by_user or registry_device.name or dev_eui)
            if registry_device
            else (
                runtime_device.device_name
                or runtime_device.device_id
                or runtime_device.dev_eui
            )
        ),
        "model": (
            registry_device.model if registry_device else runtime_device.device_type
        ),
        "manufacturer": (
            registry_device.manufacturer if registry_device else "LoRaWAN"
        ),
        "sw_version": (
            registry_device.sw_version
            if registry_device
            else runtime_device.application_name
        ),
        "application_name": (
            runtime_device.application_name if runtime_device else None
        ),
        "identifiers": sorted(identifiers),
        "entry_id": entry.entry_id if entry else None,
        "connection_name": _entry_name(entry) if entry else None,
        "connection_color": (
            _connection_color(entry, entry_index) if entry else None
        ),
        "online": runtime.is_device_online(dev_eui) if runtime else False,
        "last_uplink_at": (
            runtime.last_seen_by_device.get(clean_dev_eui) if runtime else None
        ),
        "available_entities": available_entities,
        "tile_value_keys": selected_tile_values,
        "climate_entities": climate_overrides.get(clean_dev_eui, []),
        "tile_values": [
            entities_by_id[entity_id]
            for entity_id in selected_tile_values
            if entity_id in entities_by_id
        ],
        "offline_after_hours": offline_overrides.get(
            clean_dev_eui, default_offline_after
        ),
        "offline_after_default_hours": default_offline_after,
        "create_raw_sensors": raw_overrides.get(
            clean_dev_eui, config.get(CONF_CREATE_RAW_SENSORS, True)
        ),
        "create_remaining_sensors": remaining_overrides.get(
            clean_dev_eui, config.get(CONF_CREATE_REMAINING_SENSORS, False)
        ),
    }


def _panel_device_entities(hass, entity_registry, device_id) -> list[dict]:
    """Return enabled, JSON-safe registry entities for one device."""
    if not device_id:
        return []
    entities = []
    for entity in entity_registry.entities.values():
        if entity.device_id != device_id or entity.disabled_by is not None:
            continue
        state = hass.states.get(entity.entity_id)
        attributes = state.attributes if state else {}
        name = str(
            entity.name
            or entity.original_name
            or attributes.get("friendly_name")
            or entity.entity_id
        )
        device_class = attributes.get("device_class") or getattr(
            entity, "original_device_class", None
        )
        entities.append(
            {
                "entity_id": entity.entity_id,
                "unique_id": entity.unique_id,
                "domain": entity.entity_id.partition(".")[0],
                "name": name,
                "state": state.state if state else "unavailable",
                "unit": attributes.get("unit_of_measurement"),
                "min": attributes.get("min", attributes.get("min_temp")),
                "max": attributes.get("max", attributes.get("max_temp")),
                "step": attributes.get(
                    "step", attributes.get("target_temp_step")
                ),
                "target_temperature": attributes.get("temperature"),
                "current_temperature": attributes.get("current_temperature"),
                "supported_features": attributes.get("supported_features", 0),
                "options": list(attributes.get("options") or []),
                "device_class": str(device_class) if device_class else None,
            }
        )
    entities.sort(key=lambda item: item["name"].lower())
    return entities


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
    runtimes = hass.data.get(DOMAIN, {})
    clean_dev_eui = _clean_dev_eui(msg["dev_eui"])
    runtime = next(
        (
            candidate
            for candidate in runtimes.values()
            if clean_dev_eui in candidate.devices
        ),
        None,
    )
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
    _sync_entry_title(hass, entry)
    _remove_obsolete_remaining_entities(hass, entry)
    runtime = LoRaWANRuntime(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime

    await runtime.async_start()
    _remove_stale_downlink_entities(hass, entry, runtime)
    _remove_stale_climate_entities(hass, entry)
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


def _remove_stale_climate_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove composed climate entities deleted in the device settings."""
    data = dict(entry.data)
    data.update(entry.options)
    valid = {
        f"{entry.entry_id}_{_clean_dev_eui(dev_eui)}_climate_{definition['id']}"
        for dev_eui, definitions in (
            data.get(CONF_DEVICE_CLIMATE_ENTITIES) or {}
        ).items()
        if isinstance(definitions, list)
        for definition in definitions
        if isinstance(definition, dict) and definition.get("id")
    }
    registry = er.async_get(hass)
    marker = f"{entry.entry_id}_"
    for entity in list(registry.entities.values()):
        if (
            entity.config_entry_id == entry.entry_id
            and entity.domain == "climate"
            and entity.unique_id.startswith(marker)
            and "_climate_" in entity.unique_id
            and entity.unique_id not in valid
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


def _connection_color(entry: ConfigEntry, index: int) -> str:
    """Return a safe CSS color for a config entry."""
    channels = _connection_color_channels(entry, index)
    return f"rgb({channels[0]}, {channels[1]}, {channels[2]})"


def _connection_color_channels(entry: ConfigEntry, index: int) -> list[int]:
    """Return validated RGB channels for a config entry."""
    data = dict(entry.data)
    data.update(entry.options)
    palette = (
        DEFAULT_CONNECTION_COLOR,
        [156, 39, 176],
        [255, 152, 0],
        [0, 150, 136],
        [233, 30, 99],
        [63, 81, 181],
    )
    color = data.get(CONF_CONNECTION_COLOR) or palette[index % len(palette)]
    if not isinstance(color, (list, tuple)) or len(color) != 3:
        color = palette[index % len(palette)]
    try:
        channels = [max(0, min(255, int(channel))) for channel in color]
    except (TypeError, ValueError):
        channels = list(palette[index % len(palette)])
    return channels


def _entry_name(entry: ConfigEntry) -> str:
    """Return the configured clear-text name without the native-page emoji."""
    data = dict(entry.data)
    data.update(entry.options)
    return str(data.get(CONF_NAME) or entry.title)


def _sync_entry_title(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Apply the configured color marker to new and legacy config entries."""
    entries = hass.config_entries.async_entries(DOMAIN)
    index = next(
        (position for position, item in enumerate(entries) if item.entry_id == entry.entry_id),
        0,
    )
    title = _colored_entry_title(
        _entry_name(entry),
        _connection_color_channels(entry, index),
    )
    if entry.title != title:
        hass.config_entries.async_update_entry(entry, title=title)


def _colored_entry_title(name: str, color: list[int]) -> str:
    """Return a config-entry title marked with its approximate color family."""
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
