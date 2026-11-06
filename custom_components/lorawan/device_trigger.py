"""Device automation facade for integration-calculated uplink events."""
import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.components.homeassistant.triggers import event
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .uplink_scheduler import EVENT

TRIGGER_TYPE = "uplink_schedule"
TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend({
    vol.Required(CONF_TYPE): vol.In({TRIGGER_TYPE}),
})


async def async_get_triggers(hass, device_id):
    device = dr.async_get(hass).async_get(device_id)
    if device is None or not any(domain == DOMAIN for domain, _ in device.identifiers):
        return []
    return [{CONF_PLATFORM: "device", CONF_DOMAIN: DOMAIN,
             CONF_DEVICE_ID: device_id, CONF_TYPE: TRIGGER_TYPE}]


async def async_attach_trigger(hass, config, action, trigger_info):
    event_config = event.TRIGGER_SCHEMA({
        CONF_PLATFORM: "event", "event_type": EVENT,
        "event_data": {CONF_DEVICE_ID: config[CONF_DEVICE_ID]},
    })
    return await event.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
