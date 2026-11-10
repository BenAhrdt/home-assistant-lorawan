"""Home Assistant lifecycle and event bridge for integration-calculated triggers."""
from datetime import UTC, datetime

from homeassistant.core import callback
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.storage import Store

from .const import DOMAIN, device_identifier
from .control_references import entity_references
from .uplink_schedule import DEFAULTS, UplinkSchedule

EVENT = "lorawan_uplink_schedule"
SIGNAL = "lorawan_uplink_schedule_updated"


class UplinkScheduler:
    """Own independent per-device timers; never send a downlink."""

    def __init__(self, runtime):
        self.runtime = runtime
        self.hass = runtime.hass
        self.settings = {}
        self.states = {}
        self.plans = {}
        self.last_fired = {}
        self.timers = {}
        self.store = Store(self.hass, 1, f"lorawan_uplink_schedule_{runtime.entry.entry_id}")

    async def async_load(self):
        data = await self.store.async_load() or {}
        self.settings = data.get("settings", {})

    def config(self, dev_eui):
        return {**DEFAULTS, **self.settings.get(dev_eui, {})}

    async def async_configure(self, dev_eui, key, value):
        settings = self.config(dev_eui)
        if key == "mode":
            if value not in {"disabled", "automatic", "after_uplink"}:
                raise ValueError("Unknown uplink schedule mode")
        elif key in {"lead_seconds", "delay_seconds", "minimum_seconds"}:
            value = float(value)
            if not 1 <= value <= 604800:
                raise ValueError("Seconds must be between 1 and 604800")
        else:
            raise ValueError("Unknown uplink schedule setting")
        settings[key] = value
        self.settings[dev_eui] = settings
        self.cancel(dev_eui)
        self.states.pop(dev_eui, None)
        self.plans.pop(dev_eui, None)
        await self.store.async_save({"settings": self.settings})
        self.notify(dev_eui)

    def cancel(self, dev_eui):
        if unsub := self.timers.pop(dev_eui, None):
            unsub()

    def stop(self):
        for dev_eui in list(self.timers):
            self.cancel(dev_eui)

    def notify(self, dev_eui):
        async_dispatcher_send(self.hass, SIGNAL, self.runtime.entry.entry_id, dev_eui)

    @callback
    def observe(self, dev_eui):
        settings = self.config(dev_eui)
        if settings["mode"] == "disabled":
            return
        plan = self.states.setdefault(dev_eui, UplinkSchedule()).observe(
            datetime.now(UTC), settings
        )
        if plan is None:
            return
        self.cancel(dev_eui)
        self.plans[dev_eui] = plan
        if plan["scheduled_for"] is not None:
            @callback
            def fire(now):
                self.timers.pop(dev_eui, None)
                device = self.runtime.devices.get(dev_eui)
                if device is None:
                    return
                registry_device = dr.async_get(self.hass).async_get_device(
                    identifiers={(DOMAIN, device_identifier(self.runtime.entry.entry_id, dev_eui))}
                )
                if registry_device is None:
                    return
                area = ar.async_get(self.hass).async_get_area(registry_device.area_id) if registry_device.area_id else None
                data = {key: value.isoformat() if isinstance(value, datetime) else value
                        for key, value in plan.items()}
                device_name = (
                    registry_device.name_by_user
                    or registry_device.name
                    or device.device_name
                )
                entries = er.async_entries_for_device(
                    er.async_get(self.hass), registry_device.id
                )
                references = entity_references(
                    self.runtime, dev_eui, registry_device.id, entries
                )
                triggered_at = now.isoformat()
                data.update(source=DOMAIN, device_id=registry_device.id,
                            device_name=device_name,
                            dev_eui=dev_eui, config_entry_id=self.runtime.entry.entry_id,
                            area_id=registry_device.area_id,
                            area_name=area.name if area else None,
                            schema_version=1,
                            trigger_id=(
                                f"{self.runtime.entry.entry_id}:{dev_eui}:{triggered_at}"
                            ),
                            triggered_at=triggered_at,
                            controls=references["controls"],
                            entities=references,
                            device={
                                "ha_device_id": registry_device.id,
                                "lorawan_device_id": device.device_id,
                                "dev_eui": dev_eui,
                                "name": device_name,
                                "network_name": device.device_name,
                                "device_type": device.device_type,
                                "area_id": registry_device.area_id,
                                "area_name": area.name if area else None,
                                "config_entry_id": self.runtime.entry.entry_id,
                                "network": device.network,
                                "application_id": device.application_id,
                                "application_name": device.application_name,
                            },
                            schedule={
                                key: data.get(key)
                                for key in (
                                    "mode",
                                    "interval_seconds",
                                    "offset_seconds",
                                    "last_uplink",
                                    "expected_next_uplink",
                                    "scheduled_for",
                                )
                            })
                self.last_fired[dev_eui] = now
                self.hass.bus.async_fire(EVENT, data)
                self.notify(dev_eui)
            self.timers[dev_eui] = async_track_point_in_utc_time(self.hass, fire, plan["scheduled_for"])
        self.notify(dev_eui)
