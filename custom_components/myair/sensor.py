from .const import DOMAIN, MYAIR_ZONE_OPEN, MYAIR_ZONE_CLOSE

from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    return True

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up MyAir sensor platform."""
    
    my = hass.data[DOMAIN][config_entry.data.get('url')]

    if('aircons' in my.coordinator.data):
        entities = []
        for _, acx in enumerate(my.coordinator.data['aircons']):
            for _, zx in enumerate(my.coordinator.data['aircons'][acx]['zones']):
                # Only show damper sensors when zone is in temperature control
                if(my.coordinator.data['aircons'][acx]['zones'][zx]['type'] != 0):
                    entities.append(MyAirZoneVent(my, acx, zx))
                # Only show wireless signal strength sensors when using wireless sensors
                if(my.coordinator.data['aircons'][acx]['zones'][zx]['rssi'] > 0):
                    entities.append(MyAirZoneSignal(my, acx, zx))
        async_add_entities(entities)   
    return True
         

class MyAirZoneVent(Entity):

    def __init__(self, my, acx, zx):
        self.extend(my)
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
        if(self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == MYAIR_ZONE_OPEN):
            return self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['value']
        else:
            return 0

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def icon(self):
        return ["mdi:fan-off","mdi:fan"][self.coordinator.data['aircons'][self.acx]['zones'][self.zx]['state'] == MYAIR_ZONE_OPEN]

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

    def __init__(self, my, acx, zx):
        self.extend(my)
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