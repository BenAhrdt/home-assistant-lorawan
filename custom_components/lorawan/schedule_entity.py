"""Visible controls and timestamps for integration-generated uplink schedules."""
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SIGNAL_DEVICE_ADDED, device_identifier
from .runtime import add_runtime_listener
from .uplink_scheduler import SIGNAL


@callback
def setup_schedule_entities(runtime, entry, async_add_entities, platform):
    """Add controls to existing and subsequently discovered devices."""
    added = set()

    @callback
    def add(dev_eui):
        if dev_eui in added:
            return
        added.add(dev_eui)
        if platform == "select":
            entities = [ScheduleMode(runtime, dev_eui, "mode")]
        elif platform == "number":
            entities = [ScheduleNumber(runtime, dev_eui, key)
                        for key in ("lead_seconds", "delay_seconds", "minimum_seconds")]
        else:
            entities = [ScheduleTimestamp(runtime, dev_eui, key)
                        for key in ("scheduled_for", "expected_next_uplink", "last_fired")]
        async_add_entities(entities)

    for dev_eui in runtime.devices:
        add(dev_eui)
    entry.async_on_unload(add_runtime_listener(runtime.hass, SIGNAL_DEVICE_ADDED, entry.entry_id, add))


class ScheduleEntity(Entity):
    """A calculation belonging to the integration, associated with a device."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_icon = "mdi:timer-outline"

    def __init__(self, runtime, dev_eui, key):
        self.runtime = runtime
        self.dev_eui = dev_eui
        self.key = key
        self._attr_unique_id = f"{runtime.entry.entry_id}_{dev_eui}_uplink_schedule_{key}"
        self._attr_translation_key = f"uplink_schedule_{key}"

    @property
    def scheduler(self):
        return self.runtime.uplink_scheduler

    @property
    def device_info(self):
        return {"identifiers": {(DOMAIN, device_identifier(self.runtime.entry.entry_id, self.dev_eui))}}

    @property
    def extra_state_attributes(self):
        return {"source": "lorawan", "calculated_by_integration": True}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()

        @callback
        def update(dev_eui):
            if dev_eui == self.dev_eui:
                self.async_write_ha_state()

        self.async_on_remove(add_runtime_listener(self.hass, SIGNAL, self.runtime.entry.entry_id, update))


class ScheduleMode(ScheduleEntity, SelectEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_options = ["disabled", "automatic", "after_uplink"]

    @property
    def current_option(self):
        return self.scheduler.config(self.dev_eui)["mode"]

    async def async_select_option(self, option):
        await self.scheduler.async_configure(self.dev_eui, "mode", option)


class ScheduleNumber(ScheduleEntity, NumberEntity):
    _attr_entity_category = EntityCategory.CONFIG
    _attr_native_unit_of_measurement = "s"
    _attr_native_min_value = 1
    _attr_native_max_value = 604800
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    @property
    def native_value(self):
        return self.scheduler.config(self.dev_eui)[self.key]

    async def async_set_native_value(self, value):
        await self.scheduler.async_configure(self.dev_eui, self.key, value)


class ScheduleTimestamp(ScheduleEntity, SensorEntity):
    _attr_entity_registry_enabled_default = False
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self):
        if self.key == "last_fired":
            return self.scheduler.last_fired.get(self.dev_eui)
        plan = self.scheduler.plans.get(self.dev_eui, {})
        value = plan.get(self.key)
        if self.key == "scheduled_for" and self.dev_eui not in self.scheduler.timers:
            return None
        return value
