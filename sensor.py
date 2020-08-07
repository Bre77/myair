from .const import (
    DOMAIN,
)

from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up MyAir sensor platform."""
    
    coordinator = hass.data[DOMAIN]['coordinator']

    if('aircons' in coordinator.data):
        entities = []
        for _, acx in enumerate(coordinator.data['aircons']):
            for _, zx in enumerate(coordinator.data['aircons'][acx]['zones']):
                if('value' in coordinator.data['aircons'][acx]['zones'][zx]):
                    entities.append(MyAirZoneVent(hass, acx, zx))
                if('rssi' in coordinator.data['aircons'][acx]['zones'][zx]):
                    entities.append(MyAirZoneSignal(hass, acx, zx))
        async_add_entities(entities)
    return True
             

class MyAirZoneVent(Entity):

    def __init__(self, hass, acx, zx):
        self.coordinator = hass.data[DOMAIN]['coordinator']
        self.device = hass.data[DOMAIN]['device']
        self.acx = acx
        self.zx = zx

    @property
    def name(self):
        return f"{self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['name']} Vent"

    @property
    def unique_id(self):
        return f"{self.acx}-{self.zx}-vent"

    @property
    def state(self):
        if(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == 'open'):
            return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['value']
        else:
            return 0

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def icon(self):
        return ["mdi:fan-off","mdi:fan"][self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == 'open']

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return self.device

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()

class MyAirZoneSignal(Entity):

    def __init__(self, hass, acx, zx):
        self.coordinator = hass.data[DOMAIN]['coordinator']
        self.device = hass.data[DOMAIN]['device']
        self.acx = acx
        self.zx = zx

    @property
    def name(self):
        return f"{self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['name']} Signal"

    @property
    def unique_id(self):
        return f"{self.acx}-{self.zx}-signal"

    @property
    def state(self):
        return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['rssi']

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def icon(self):
        if(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['rssi'] >= 80):
            return "mdi:wifi-strength-4"
        elif(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['rssi'] >= 60):
            return "mdi:wifi-strength-3"
        elif(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['rssi'] >= 40):
            return "mdi:wifi-strength-2"
        elif(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['rssi'] >= 20):
            return "mdi:wifi-strength-1"
        else:
            return "mdi:wifi-strength-outline"

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return self.device

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()